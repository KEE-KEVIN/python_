import json

import redis
import pymongo
import pymysql


class MongoClient(object):

    def __init__(self, addr=None, db=None, port=None, user=None, passwd=None):
        config = self.get_mongo_config(addr, db, port, user, passwd)
        client = pymongo.MongoClient(config['host'])
        self.client = client
        self.active_db = self.use_database(config.get('name'))

    def use_database(self, database_name):
        if not database_name:
            return None
        return self.client[database_name]

    def get_mongo_config(self, addr=None, db=None, port=None, user=None, passwd=None):
        if user and passwd:
            host = "mongodb://{}:{}@{}:{}/{}".format(user, passwd, addr, port, db)
        else:
            host = "mongodb://{}:{}".format(addr, port)
        return {
            'host': host,
            'maxPoolSize': 1000,
            'tz_aware': True,
            'socketTimeoutMS': None,
            'connectTimeoutMS': 1000,
            'w': 1,
            'wtimeout': 10000,
            'j': False,
            'name': db
        }

    def close(self):
        self.client.close()


class MySQLClient(object):

    def __init__(self, addr=None, db=None, user=None, pwd=None, port=3306):
        settings = self.get_mysql_config(addr, port, db, user, pwd)
        self.conn = pymysql.connect(**settings)

    @property
    def connect(self):
        return self.conn

    def get_mysql_config(self, addr=None, port=3306, db=None, user=None, passwd=None):
        return {
            "host": "{}".format(addr),
            "user": "{}".format(user),
            "passwd": "{}".format(passwd),
            "db": "{}".format(db),
            "charset": "utf8",
            'port': int(port),
            'autocommit': True
        }

    def execute_noquery_cmd(self, cmd: str, args=None, connect=None, callback=None):
        connect = connect or self.connect
        with connect.cursor() as cursor:
            r = cursor.execute(cmd, args)
            if not connect.autocommit_mode:
                connect.commit()
            if callback:
                callback(cmd, args, connect, cursor)
            return r

    def execute_noquery_many(self, cmd: str, *args, connect=None, callback=None):
        connect = connect or self.connect
        with connect.cursor() as cursor:
            r = cursor.executemany(cmd, list(args))
            if not connect.autocommit_mode:
                connect.commit()
            if callback:
                callback(cmd, args, connect, cursor)
            return r

    def query(self, cmd: str, args=None, connect=None, fetchall=False):
        result = []

        def query_callback(cmd, args, connect, cursor):
            if not fetchall:
                result.append(cursor.fetchone())
            else:
                result.extend(cursor.fetchall())

        self.execute_noquery_cmd(cmd, args, connect, query_callback)
        if not result:
            return None
        elif not fetchall:
            return result[0]
        else:
            return result

    def query_many(self, *cmdArgPairs, connect=None, fetchall=False) -> iter:
        connect = connect or self.connect
        with connect.cursor() as cursor:
            for cmd, args in cmdArgPairs:
                cursor.execute(cmd, args)
                if not connect.autocommit_mode:
                    connect.commit()
                if fetchall:
                    func = cursor.fetchall
                else:
                    func = cursor.fetchone
                yield func()

    def transaction(self, *cmdArgs, connect=None):
        connect = connect or self.connect
        cursor = connect.cursor()
        try:
            for cmd, args in cmdArgs:
                cursor.execute(cmd, args)
        except Exception as ex:
            connect.rollback()
        else:
            if not connect.autocommit_mode:
                connect.commit()
        finally:
            cursor.close()

    def close(self, conn=None):
        conn = conn or self.connect
        conn.close()


class Redis(object):

    def __init__(self, host=None, port=None,
                 db=None, password=None, socket_timeout=None,
                 socket_connect_timeout=None):
        self._default_client = self.get_db(
            host, port, db, password, socket_timeout, socket_connect_timeout)

    @property
    def client(self):
        return self._default_client

    def keys(self, pattern=None, redis_db=None):
        client = self.client or redis_db
        return self.client.keys(pattern or "*")

    def get_db(self, host='localhost', port=6379, db=0,
               password=None, socket_timeout=None, socket_connect_timeout=None):
        return redis.Redis(
            host, port, db, password, socket_timeout, socket_connect_timeout)

    def del_key(self, keynames, redis_db=None):
        client = self.client or redis_db
        if isinstance(keynames, str):
            keynames = [keynames]
        return client.delete(*keynames)

    def exists(self, keyname, redis_db=None):
        client = self.client or redis_db
        return client.exists(keyname)

    def serialize(self, data):
        if not isinstance(data, str):
            return json.dumps(data)
        return data

    def deserialize(self, data):
        if not isinstance(data, str):
            return data
        try:
            s = json.loads(data)
        except:
            s = data
        return s

    def set(self, keyname, value, expire_sec=None, redis_db=None):
        client = self.client or redis_db
        data = self.serialize(value)
        return client.set(keyname, data, ex=expire_sec)

    def get(self, keyname, redis_db=None):
        client = self.client or redis_db
        data = client.get(keyname)
        return self.deserialize(data)

    def set_add(self, keyname, *value, expire_sec=None, redis_db=None):
        client = self.client or redis_db
        return client.sadd(keyname, *value)

    def m_set(self, key_value: dict):
        return self.client.mset(key_value)

    def get_set(self, token, value):
        return self.client.set(token, value)


class AliveRedis(Redis):
    """
    连接keep alive
    os: linux
    version: 大于2.4
    """

    def get_db(self, host='localhost', port=6379, db=0,
               password=None, socket_timeout=None, socket_connect_timeout=None):
        pool = redis.ConnectionPool(host=host, port=port, password=password,
                                    db=db, socket_connect_timeout=socket_connect_timeout,
                                    socket_timeout=socket_timeout, socket_keepalive=True,
                                    )
        return redis.Redis(connection_pool=pool)

    def add_hash(self, token, key_value):
        return self.client.hmset(token, key_value)

    def set_hash(self, token, key, value):
        return self.client.hset(name=token, key=key, value=value)

    def get_hash(self, token, key):
        return self.client.hget(token, key)


class MG(object):
    def __init__(self, address=None, db=None, port=None, user=None, pwd=None):
        config = self.get_mongodb_config(address, db, port, user, pwd)
        self.client = pymongo.MongoClient(config['host'])
        self.db = self.use_database(config.get('name'))

    def use_database(self, database_name):
        if not database_name:
            return None
        return self.client[database_name]

    @staticmethod
    def get_mongodb_config(address=None, db=None, port=None, user=None, pwd=None):
        if user and pwd:
            host = "mongodb://{}:{}@{}:{}/{}".format(user, pwd, address, port, db)
        else:
            host = "mongodb://{}:{}".format(address, port)
        return {
            'host': host,
            'maxPoolSize': 1000,
            'tz_aware': True,
            'socketTimeoutMS': None,
            'connectTimeoutMS': 1000,
            'w': 1,
            'wtimeout': 10000,
            'j': False,
            'name': db
        }


class BaseHandle(object):
    @staticmethod
    def insert_one(collection, data: dict):
        """直接使用insert() 可以插入一条和插入多条 不推荐 明确区分比较好"""
        res = collection.insert_one(data)
        return res.inserted_id

    @staticmethod
    def insert_many(collection, data_list):
        res = collection.insert_many(data_list)
        return res.inserted_ids

    @staticmethod
    def find_one(collection, data, data_field: dict):
        if len(data_field):
            res = collection.find_one(data, data_field)
        else:
            res = collection.find_one(data)
        return res

    @staticmethod
    def find_many(collection, data, data_field: dict):
        """ data_field 是指输出 操作者需要的字段"""
        if len(data_field):
            res = collection.find(data, data_field)
        else:
            res = collection.find(data)
        return res

    @staticmethod
    def update_one(collection, data_condition, data_set):
        """修改一条数据"""
        res = collection.update_one(data_condition, data_set)
        return res

    @staticmethod
    def update_many(collection, data_condition, data_set):
        """ 修改多条数据 """
        res = collection.update_many(data_condition, data_set)
        return res

    @staticmethod
    def replace_one(collection, data_condition, data_set):
        """ 完全替换掉 这一条数据， 只是 _id 不变"""
        res = collection.replace_one(data_condition, data_set)
        return res

    @staticmethod
    def delete_many(collection, data):
        res = collection.delete_many(data)
        return res

    @staticmethod
    def delete_one(collection, data):
        res = collection.delete_one(data)
        return res

    @staticmethod
    def count(collection, data):
        res = collection.find(data).count()
        return res

    @staticmethod
    def count_aggregate(collection, data):
        res = collection.aggregate(data)
        count = list(res)
        return count[0].get("total", 0) if count else 0

    @staticmethod
    def aggregate(collection, data):
        res = collection.aggregate(data)
        return res


class DBBase(object):
    """ 各种query 中的数据 data 和 mongodb 文档中的一样"""

    def __init__(self, address, db, port, user=None, pwd=None):
        self.mg = MG(address, db, port, user, pwd)

    def insert_one(self, collection, data):
        collection = self.mg.db[collection]
        res = BaseHandle.insert_one(collection, data)
        return res

    def insert_many(self, collection, data_list):
        collection = self.mg.db[collection]
        res = BaseHandle.insert_many(collection, data_list)
        print("Successfully insert!")
        return res

    def find_one(self, collection, data, data_field: dict):
        collection = self.mg.db[collection]
        res = BaseHandle.find_one(collection, data, data_field)
        return res

    def find_many(self, collection, data, data_field: dict):
        """ 有多个键值的话就是 AND 的关系"""
        collection = self.mg.db[collection]
        res = BaseHandle.find_many(collection, data, data_field)
        return res

    def find_all(self, collection, data: dict, data_field: dict):
        """select * from table"""
        collection = self.mg.db[collection]
        res = BaseHandle.find_many(collection, data, data_field)
        return res

    def find_in(self, collection, field, item_list, data_field: dict):
        """SELECT * FROM inventory WHERE status in ("A", "D")"""
        collection = self.mg.db[collection]
        data = dict()
        data[field] = {"$in": item_list}
        res = BaseHandle.find_many(collection, data, data_field)
        return res

    def find_or(self, collection, data_list, data_field: dict):
        """db.inventory.find(
                {"$or": [{"status": "A"}, {"qty": {"$lt": 30}}]}
            )

        SELECT * FROM inventory WHERE status = "A" OR qty < 30
        """
        collection = self.mg.db[collection]
        data = dict()
        data["$or"] = data_list
        res = BaseHandle.find_many(collection, data, data_field)
        return res

    def find_between(self, collection, field, value1, value2, data_field: dict):
        """获取俩个值中间的数据"""
        collection = self.mg.db[collection]
        data = dict()
        data[field] = {"$gt": value1, "$lt": value2}
        # data[field] = {"$gte": value1, "$lte": value2} # <>   <= >=
        res = BaseHandle.find_many(collection, data, data_field)
        return res

    def find_more(self, collection, field, value, data_field: dict):
        collection = self.mg.db[collection]
        data = dict()
        data[field] = {"$gt": value}
        res = BaseHandle.find_many(collection, data, data_field)
        return res

    def find_less(self, collection, field, value, data_field: dict):
        collection = self.mg.db[collection]
        data = dict()
        data[field] = {"$lt": value}
        res = BaseHandle.find_many(collection, data, data_field)
        return res

    def find_like(self, collection, field, value, data_field: dict):
        """ where key like "%audio% """
        collection = self.mg.db[collection]
        data = dict()
        data[field] = {'$regex': '.*' + value + '.*'}
        print(data)
        res = BaseHandle.find_many(collection, data, data_field)
        return res

    def delete_one(self, collection, data):
        """ 删除单行数据 如果有多个 则删除第一个"""
        collection = self.mg.db[collection]
        res = BaseHandle.delete_one(collection, data)
        return res

    def delete_many(self, collection, data):
        """ 删除查到的多个数据 data 是一个字典 """
        collection = self.mg.db[collection]
        res = BaseHandle.delete_many(collection, data)
        return res

    def find_count(self, collection, query):
        collection = self.mg.db[collection]
        res = BaseHandle.count(collection, query)
        return res

    def find_count_aggregate(self, collection, query):
        collection = self.mg.db[collection]
        res = BaseHandle.count_aggregate(collection, query)
        return res

    def aggregate(self, collection, query):
        collection = self.mg.db[collection]
        res = BaseHandle.aggregate(collection, query)
        return res


SecondaryLabelMap = {
    "恶意推广-商业推广": "ad_commercialPromotion",
    "恶意推广-常用社交词汇": "ad_socialVocabulary",
    "恶意推广-广告法": "ad_advertisingLaw",
    "恶意推广-社交词汇变体": "ad_socialVariants",
    "恶意推广-违规游戏资产交易": "ad_gameTransaction",
    "恶意推广-非法资源出售": "ad_illegalResources",
    "咒骂敌视-人身攻击": "curse_personalAttacks",
    "咒骂敌视-常见脏词": "curse_badLanguage",
    "咒骂敌视-方言常见咒骂词汇": "curse_dialect",
    "咒骂敌视-消极宣泄": "curse_negativeCatharsis",
    "政治敏感-中央领导人": "politics_centralLeader",
    "政治敏感-其他涉政": "politics_other",
    "政治敏感-反党反政府实体": "politics_governmentEntities",
    "政治敏感-反党反政府言论": "politics_governmentSpeech",
    "政治敏感-国外政治相关人物": "politics_foreignPoliticians",
    "政治敏感-敏感事件": "politics_sensitiveEvent",
    "政治敏感-敏感地名": "politics_sensitiveLocation",
    "政治敏感-时事": "politics_currentEvents",
    "政治敏感-涉政拼音": "politics_pinyin",
    "政治敏感-省部级领导": "politics_provincialLeaders",
    "政治敏感-社会名人": "politics_socialCelebrities",
    "政治敏感-翻墙工具及术语": "politics_vpnTool",
    "政治敏感-英雄烈士": "politics_heroMartyrs",
    "政治敏感-落马官员": "politics_sackedOfficial",
    "政治敏感-过审补充词汇": "politics_supplementaryVocabulary",
    "政治敏感-领导人亲属": "politics_leadersRelatives",
    "文本色情-低俗词汇": "porn_vulgar",
    "文本色情-其他色情": "porn_other",
    "文本色情-性器官及用具": "porn_sexOrgans",
    "文本色情-性行为": "porn_sexualBehavior",
    "文本色情-色情资源": "porn_resources",
    "文本色情-计生情趣用品": "porn_sexToys",
    "暴恐违禁-公共安全": "terror_publicSafety",
    "暴恐违禁-其他违禁类型": "terror_other",
    "暴恐违禁-毒品与违禁药品": "terror_drugsMedicines",
    "暴恐违禁-非法代理": "terror_illegalAgent",
    "暴恐违禁-非法器械及材料": "terror_equipmentMaterials",
}




import random
import gc
import time


def random_10char(string, length):
    for i in range(length):
        y = str(random.randint(0, 9))
        string.append(y)
    string = ''.join(string)
    return string


if __name__ == '__main__':
    log_data = []
    # mongodb_config = {
    #     "address": '52.82.59.2',
    #     "port": 3306,
    #     "db": "ban_new",
    #     "collection": "sys_words",
    #     "user": "root",
    #     "pwd": "hifive2018"
    # }
    # mongodb_conn = DBBase(**mongodb_config)

    mysql_config = {
        "address": '52.82.59.2',
        "port": 3306,
        "db": "ban_new",
        "user": "root",
        "pwd": "hifive2018"
    }

    sql_client = MySQLClient(**mysql_config)

    cmd = ""


    # mongodb_conn.collection.delete_one({'id': 1})

    # for i in range(10):
    #     string = []
    #     length = 10
    #     random_id = random_10char(string, length)
    #
    #     dic = {
    #         "createdAt": int(time.time()),
    #         "logEvent": 1, "logMessage": "xxx",
    #         "expireAt": 1598003250
    #     }
    #
    #     mongodb_conn.insert_one(dic)
    #     print("Sucessfully insert data")
    #     gc.collect()
    #
    # # mongodb_conn.insert_one(log_data)
    # print("Finalizing all the data")
    # mongodb_conn.collection.create_index("expiredAt", ttl=300)
