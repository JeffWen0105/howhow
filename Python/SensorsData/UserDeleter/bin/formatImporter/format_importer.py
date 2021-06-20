#!/bin/env python3
# -*- coding: UTF-8 -*-

"""
Copyright (c) 2015 sensorsdata.cn, Inc. All Rights Reserved
@author padme(jinsilan@sensorsdata.cn)
@brief

支持各种导入
"""
import abc
import argparse
import csv
import datetime
import decimal
import hashlib
import json
import logging
import logging.handlers
import os
import pprint
import random
import re
import sys
import time
import traceback
# 忽略证书校验
import ssl
import sys as _sys

ssl._create_default_https_context = ssl._create_unverified_context

try:
    import urllib.parse as urllib
    import urllib.request as urllib2
except ImportError:
    import urllib2
    import urllib

__version__ = '1.13.7'

# build的时候会把python sdk和 pypinyin, pymysql都拷贝过来
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
import pypinyin
import sensorsanalytics

logger_name = 'format_importer'
log_file = '%s/format_importer.log' % current_dir
# 配置logger整体
logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)
formater = logging.Formatter('%(asctime)s %(lineno)d %(levelname)s %(message)s')
# 配置console 打印INFO级别
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formater)
logger.addHandler(console)


class SAArgumentParser(argparse.ArgumentParser):
    '''支持从文件读取 文件可以包含注释空行'''

    def convert_arg_line_to_args(self, arg_line):
        strip_line = arg_line.strip()
        # 空行
        if not strip_line:
            return []
        # 注释
        if strip_line.startswith('#'):
            return []
        fields = strip_line.split(':')
        # 只有一个参数 比如--debug
        if len(fields) == 1:
            return ['--%s' % fields[0]]
        # 两个参数，注意合理的strip()
        first = fields[0].strip()
        second = ':'.join(fields[1:]).strip()
        return ['--%s' % first, second]

    def _read_args_from_files(self, arg_strings):
        # expand arguments referencing files
        new_arg_strings = []
        for arg_string in arg_strings:

            # for regular arguments, just add them back into the list
            if not arg_string or arg_string[0] not in self.fromfile_prefix_chars:
                new_arg_strings.append(arg_string)

            # replace arguments referencing files with the file content
            else:
                try:
                    with open(arg_string[1:], encoding='utf-8') as args_file:
                        arg_strings = []
                        for arg_line in args_file.read().splitlines():
                            for arg in self.convert_arg_line_to_args(arg_line):
                                arg_strings.append(arg)
                        arg_strings = self._read_args_from_files(arg_strings)
                        new_arg_strings.extend(arg_strings)
                except OSError:
                    err = _sys.exc_info()[1]
                    self.error(str(err))

        # return the modified argument list
        return new_arg_strings


####
#
# 通用方法
#
###
def guess_str_type(target_str):
    '''
    为了快都是先判断长度再转的
    '''
    # 1. 按长度判断bool和datetime
    str_len = len(target_str)
    # true/false
    if str_len == 4 or str_len == 5:
        if target_str.lower() in ['true', 'false']:
            return 'bool'
    # 2010-04-03 12:00:00
    elif str_len == 19:
        try:
            datetime.datetime.strptime(target_str, '%Y-%m-%d %H:%M:%S')
            return 'datetime'
        except:
            pass
    # 2010-04-03 12:00:00.047822
    elif str_len == 26:
        try:
            datetime.datetime.strptime(target_str, '%Y-%m-%d %H:%M:%S.%f')
            return 'datetime'
        except:
            pass
    # 2010-04-03
    elif str_len == 10:
        try:
            datetime.datetime.strptime(target_str, '%Y-%m-%d')
            return 'datetime'
        except:
            pass

    # 2. 是否是数字
    try:
        float(target_str)
        return 'number'
    except:
        pass

    # 3. 都不是 则是string
    return 'string'


def format_str(target_str, str_type):
    if str_type == 'number':
        if '.' in target_str:
            return float(target_str)
        else:
            return int(target_str)
    elif str_type == 'bool':
        return target_str.lower() == 'true'
    elif str_type == 'datetime':
        if len(target_str) == 19:
            return datetime.datetime.strptime(target_str, '%Y-%m-%d %H:%M:%S')
        elif len(target_str) == 26:
            return datetime.datetime.strptime(target_str, '%Y-%m-%d %H:%M:%S.%f')
        else:
            return datetime.datetime.strptime(target_str, '%Y-%m-%d')
    else:
        return target_str


def check_url(url):
    '''
    导入url: http://xxxx:8106/sa?project=xxx
    确认url: http://xxxx:8106/debug
    '''
    debug_url = urllib.urlparse(url)
    ## 将 URI Path 替换成 Debug 模式的 '/debug'
    debug_url = debug_url._replace(path='/debug')
    logger.debug('debug url: %s' % debug_url.geturl())
    with urllib2.urlopen(debug_url.geturl()) as f:
        response = f.read().decode('utf8').strip()
        logger.debug('response: %s' % response)
        if response != 'Sensors Analytics is ready to receive your data!':
            raise Exception('invalid url %s' % url)


def parse_args():
    """
    注意几个parser的继承关系
    parent_parser -- profile_parser -- csv_profile/nginx_profile/mysql_profile
                 |-- event_parser -- csv_event/nginx_event/mysql_event
                 |-- json
    """
    # 1. 定义parser
    parent_parser = SAArgumentParser(add_help=False)
    # 公用参数
    # 1.1. url/path/project
    consumer_group = parent_parser.add_mutually_exclusive_group(required=True)
    consumer_group.add_argument('--url', '-l',
                                help='和--output_file选一个必填,发送数据的url，比如http://localhost:8106/sa, ' \
                                     '如果是云版则类似http://abc.cloud.sensorsdata.cn:8106/sa?token=xxx, ' \
                                     'token请联系我们获取. 注意这个参数和--output_file不能同时使用',
                                default=None)
    consumer_group.add_argument('--output_file', '-O',
                                help='和--url选一个必填, 输出的文件名，输出每行是一个符合格式的json。注意这个参数和--url不可同时使用',
                                default=None)
    parent_parser.add_argument('--project', '-j',
                               help='可选，指定的project名，默认是None',
                               default=None,
                               required=False)
    parent_parser.add_argument('--log_level', '-lv',
                               help='可选，指定日志输出最小等级，默认 DEBUG',
                               default='DEBUG',
                               required=False)

    # 1.2 断点续传
    parent_parser.add_argument('--skip_cnt', '-c',
                               type=int,
                               help='第一次运行请忽略，如果运行失败，需要跳过成功的那集行，这个就是指定跳过几行的',
                               default=0)
    parent_parser.add_argument('--quit_on_error', '-Q',
                               action='store_true',
                               help='如果选中，则出现一条错误日志就会退出',
                               default=False)
    parent_parser.add_argument('--debug', '-D',
                               action='store_true',
                               help='如果指定了就是使用debug模式，不会导入数据，只在stdout显示数据，参见(https://www.sensorsdata.cn/manual/debug_mode.html)',
                               default=False)

    # 2. profile/event有不同的选项
    # 2.1 profile 需要指定distinct_id
    profile_parent_parser = SAArgumentParser(add_help=False, parents=[parent_parser])
    profile_parent_parser.add_argument('--distinct_id_from', '-df',
                                       help='必填, 从哪个字段作为distinct_id，如果指定，则每条数据算作对应字段的用户的行为.',
                                       required=True)
    profile_parent_parser.add_argument('--is_login',
                                       help='可选参数, distinct_id是否是login id，默认不是.',
                                       default=False,
                                       action='store_true')

    # 2.2 event
    event_parent_parser = SAArgumentParser(add_help=False, parents=[parent_parser])
    # 指定distinct_id
    event_parent_parser.add_argument('--distinct_id_from', '-df',
                                     help='必填, 从哪个字段作为distinct_id，如果指定，则每条数据算作对应字段的用户的行为.',
                                     required=True)
    event_parent_parser.add_argument('--is_login',
                                     help='可选参数, distinct_id是否是login id，默认不是.',
                                     default=False,
                                     action='store_true')
    # event必须要么指定event_from要么指定event_default
    event_group = event_parent_parser.add_mutually_exclusive_group(required=True)
    event_group.add_argument('--event_from', '-ef',
                             help='和event_default选一个必填。哪个字段作为event名，如果指定，则每条数据的事件名为对应字段的值。')
    event_group.add_argument('--event_default', '-ed',
                             help='和event_from选一个必填。默认的event名，如果指定，则将所有数据都算作这个event的。')
    # timestammp必须要么指定timestamp_from 要么指定timestamp_default 要么都不指定
    timestamp_group = event_parent_parser.add_mutually_exclusive_group(required=False)
    timestamp_group.add_argument('--timestamp_from', '-tf',
                                 help='哪个字段作为time, 如果指定，则每条数据对应的时间为对应字段的值.')
    timestamp_group.add_argument('--timestamp_default', '-td',
                                 help='默认的timestamp, 如果指定，则将所有数据都算作这个时间的事件。')
    event_parent_parser.add_argument('--timestamp_format', '-fm',
                                     help='和timestamp_from一起使用，如果指定, 并timestamp_from对应的字段是个字符串，可以通过这种方式指定时间格式。' \
                                          '默认是%%Y-%%m-%%d %%H:%%M:%%S',
                                     default='%Y-%m-%d %H:%M:%S')

    # 2.3 item
    item_parent_parser = SAArgumentParser(add_help=False, parents=[parent_parser])
    item_parent_parser.add_argument('--item_type',
                                    help='必填，指定 item 的 item_type',
                                    required=True)
    item_parent_parser.add_argument('--item_id',
                                    help='必填，指定 item 的 item_id',
                                    required=True)

    # 2.4 signup
    signup_parent_parser = SAArgumentParser(add_help=False, parents=[parent_parser])
    signup_parent_parser.add_argument('--login_id_from',
                                      help='必填，指定用户关联的登录 ID',
                                      required=True)
    signup_parent_parser.add_argument('--anonymous_id_from',
                                      help='必填，指定用户关联的匿名 ID',
                                      required=True)

    # 3. 支持五种数据格式
    parser = SAArgumentParser(description='通用格式文件导入工具,版本号%s' % __version__)
    subparsers = parser.add_subparsers(dest='subparser_name')
    # 3.1 csv/mysql/nginx/oracle 支持分别导入event和profile
    for format_name in ['csv', 'mysql', 'nginx', 'oracle']:
        formatter_name = '%sFormatter' % format_name.title()
        formatter_class = globals()[formatter_name]
        sub_parser = subparsers.add_parser(
            '%s_profile' % format_name,
            parents=[profile_parent_parser],
            help='%s, 导入profile' % formatter_class.__doc__.splitlines()[0],
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=formatter_class.__doc__,
            fromfile_prefix_chars='@')
        formatter_class.add_parser(sub_parser)
        sub_parser = subparsers.add_parser(
            '%s_event' % format_name,
            parents=[event_parent_parser],
            help='%s, 导入event' % formatter_class.__doc__.splitlines()[0],
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=formatter_class.__doc__,
            fromfile_prefix_chars='@')
        formatter_class.add_parser(sub_parser)
        sub_parser = subparsers.add_parser(
            '%s_item' % format_name,
            parents=[item_parent_parser],
            help='%s, 导入item' % formatter_class.__doc__.splitlines()[0],
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=formatter_class.__doc__,
            fromfile_prefix_chars='@')
        formatter_class.add_parser(sub_parser)
        sub_parser = subparsers.add_parser(
            '%s_signup' % format_name,
            parents=[signup_parent_parser],
            help='%s, 导入用户关联' % formatter_class.__doc__.splitlines()[0],
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=formatter_class.__doc__,
            fromfile_prefix_chars='@')
        formatter_class.add_parser(sub_parser)
    # 3.2 json直接继承parent parser 不区分event/profile/item
    sub_parser = subparsers.add_parser(
        'json',
        parents=[parent_parser],
        help=JsonFormatter.__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=JsonFormatter.__doc__,
        fromfile_prefix_chars='@')
    JsonFormatter.add_parser(sub_parser)

    # 4. 解析
    args = parser.parse_args()
    if not args.subparser_name:
        parser.print_help()
        sys.exit(1)
    return args


######
#
# 从这里开始各个formater的实现
#
######
class BaseFormatter(object):
    def __init__(self, args, lib_detail):
        '''初始化方法'''
        self.args = args
        self.is_event = args.subparser_name.endswith('_event')
        self.is_item = args.subparser_name.endswith('_item')
        self.is_signup = args.subparser_name.endswith('_signup')
        # 如果是event 获取event和time的方式需要根据传递参数来判断
        # event 两种
        if self.is_event:
            if args.event_from:
                self.get_event = self.__get_event_from_record
            else:
                self.get_event = self.__get_default_event
            # time 三种
            if args.timestamp_from:
                self.get_timestamp = self.__get_timestamp_from_record
            elif args.timestamp_default:
                self.get_timestamp = self.__get_default_timestamp
            else:
                self.get_timestamp = self.__get_current_timestamp
        # 发送的方式取决于是event还是profile 调用不同的方法 注意json是不区分event profile的
        self.send = self.send_event if self.is_event else self.send_profile
        # 发送 item
        if self.is_item:
            self.send = self.send_item
        # 发送 signup
        if self.is_signup:
            self.send = self.send_signup

        # 过滤掉用于获取event/time/user的列
        if self.is_item:
            self.skip_cols = [args.item_type]
            self.skip_cols.append(args.item_id)
        elif self.is_signup:
            self.skip_cols = [args.login_id_from]
            self.skip_cols.append(args.anonymous_id_from)
        else:
            self.skip_cols = [args.distinct_id_from]
            if self.is_event:
                if args.event_from:
                    self.skip_cols.append(args.event_from)
                if args.timestamp_from:
                    self.skip_cols.append(args.timestamp_from)
        # 记录导入信息的
        lib_detail_title = {'mysql': 'MySQL', 'csv': 'csv', 'nginx': 'Nginx', 'oracle': 'Oracle'}[
            args.subparser_name.split('_')[0]]
        self.default_properties = {
            '$lib': 'FormatImporter',
            '$lib_version': __version__,
            '$lib_method': 'tools',
            '$lib_detail': ('%s##%s' % (lib_detail_title, lib_detail))[:100],
        }

    def set_consumer(self, consumer):
        self.sa = sensorsanalytics.SensorsAnalytics(consumer, self.args.project, True)
        self.sa.register_super_properties({
            '$lib': self.default_properties['$lib'],
            '$lib_version': self.default_properties['$lib_version']
        })
        self.sa._get_lib_properties = lambda: self.default_properties

    def get_distinct_id(self, record):
        """获取distinct_id 只有一种方式 就是使用传递参数的字段名"""
        if self.args.distinct_id_from not in record:
            raise Exception('cannot find distinct_id[%s] in record[%s]' \
                            % (self.args.distinct_id_from, record))
        return record[self.args.distinct_id_from]

    def get_item_type(self, record):
        if self.args.item_type not in record:
            raise Exception('cannot find item_type[%s] in record[%s]' \
                            % (self.args.item_type, record))
        return record[self.args.item_type]

    def get_item_id(self, record):
        if self.args.item_id not in record:
            raise Exception('cannot find item_id[%s] in record[%s]' \
                            % (self.args.item_id, record))
        return record[self.args.item_id]

    def get_login_id(self, record):
        if self.args.login_id_from not in record:
            raise Exception('cannot find login_id[%s] in record[%s]' \
                            % (self.args.login_id_from, record))
        return record[self.args.login_id_from]

    def get_anonymous_id(self, record):
        if self.args.anonymous_id_from not in record:
            raise Exception('cannot find anonymous_id[%s] in record[%s]' \
                            % (self.args.anonymous_id_from, record))
        return record[self.args.anonymous_id_from]

    def __get_event_from_record(self, record):
        """获取event 方式一 使用传递参数的字段名"""
        if self.args.event_from not in record:
            raise Exception('cannot find event[%s] in record[%s]' % (self.args.event_from, record))
        return record[self.args.event_from]

    def __get_default_event(self, record):
        """获取event 方式二 使用传递参数的默认值"""
        return self.args.event_default

    def __get_timestamp_from_record(self, record):
        """获取time 方式一 使用传递参数的字段名"""
        if self.args.timestamp_from not in record:
            raise Exception('cannot find timestamp[%s] in record[%s]' % (self.args.timestamp_from, record))
        elif type(record[self.args.timestamp_from]) is str:
            return datetime.datetime.strptime(record[self.args.timestamp_from], self.args.timestamp_format)
        else:
            return record[self.args.timestamp_from]

    def __get_default_timestamp(self, record):
        """获取time 方式二 使用传递参数的默认值"""
        return datetime.datetime.strptime(self.args.timestamp_default, self.args.timestamp_format)

    def __get_current_timestamp(self, record):
        """获取time 方式三 使用当前时间"""
        return datetime.datetime.now()

    @classmethod
    @abc.abstractmethod
    def add_parser(cls, sub_parser):
        '''初始化sub_parser'''
        pass

    @abc.abstractmethod
    def get_total_num(self):
        '''返回总条数 返回-1表示无法获取总条数 则不计算进度'''
        pass

    @abc.abstractmethod
    def read_records(self):
        '''返回一行'''
        pass

    @abc.abstractmethod
    def parse_record(self, record):
        '''解析一行，注意和上面区分 便于异常处理'''
        pass

    @abc.abstractmethod
    def parse_property(self, record):
        '''解析properties'''
        pass

    def send_event(self, record):
        '''发送event'''
        event = self.get_event(record)
        distinct_id = self.get_distinct_id(record)
        timestamp = self.get_timestamp(record)
        properties = self.parse_property(record)
        properties['$time'] = timestamp
        self.sa.track(distinct_id, event, properties, is_login_id=self.args.is_login)

    def send_profile(self, record):
        '''发送profile'''
        distinct_id = self.get_distinct_id(record)
        properties = self.parse_property(record)
        self.sa.profile_set(distinct_id, properties, is_login_id=self.args.is_login)

    def send_item(self, record):
        item_type = str(self.get_item_type(record))
        item_id = str(self.get_item_id(record))
        properties = self.parse_property(record)
        self.sa.item_set(item_type=item_type, item_id=item_id, properties=properties)

    def send_signup(self, record):
        login_id = str(self.get_login_id(record))
        anonymous_id = str(self.get_anonymous_id(record))
        self.sa.track_signup(login_id, anonymous_id)

    def close(self):
        '''清理方法'''
        self.sa.close()


class CsvFormatter(BaseFormatter):
    """将csv格式文件导入
使用举例:
    1. format_importer.py csv_event -l 'http://localhost:8006/sa' -ef event -df user -td '2014-08-01 12:00:00'
       -u admin -p passwd -f ./test.csv -w 'http://localhost:8007'
       将test.csv中所有列作为properties导入本地的私有部署版本，其中每行是一个事件，event对应的列为事件名，
       user对应的列为distinct_id, 时间全部为2014-08-01 12:00:00
    2. format_importer.py csv_event -l 'http://localhost:8006/sa' -ed my_event -df user -tf time -fm '%Y%m%d%H%M%S'
       -u admin -p passwd -f ./test.csv -w 'http://localhost:8007' -pl col1,col2,col3
       将test.csv中(col1, col2, col3)作为properties导入本地的私有部署版本，对应事件名全部为my_event,
       每行是一个事件，user对应的列为distinct_id, time对应的列为time(格式类似20150130125959)
    3. format_importer.py csv_profile -l 'http://localhost:8006/sa' -df user -u admin -p passwd -f
       ./test.csv -w 'http://localhost:8007'
       将test.csv中所有的列作为用户属性导入本地的私有部署版本，其中没一行是一个用户，user对应的列为distinct_id
    4. format_importer.py csv_event @./conf/csv_event.conf
       也可以修改conf/csv_event.conf和conf/csv_profile.conf来填写所有必要参数
    """
    ename_pattern = re.compile(r'[\$]{0,1}[a-zA-Z0-9_]+$')

    def __init__(self, args):
        '''初始化方法'''
        super().__init__(args, args.filename)
        # 1. 参数校验
        skip_identify_list = args.skip_identify.split(',') if args.skip_identify else []
        property_list = args.property_list.split(',') if args.property_list else []
        csv_params = {}
        for arg, name in [(args.csv_delimiter, 'delimiter'), (args.csv_quotechar, 'quotechar')]:
            if len(arg) == 1:
                csv_params[name] = arg
            elif arg[0] == '\\' and arg[1:].isdecimal():
                csv_params[name] = chr(int(arg[1:]))
        self.ignore_value = args.ignore_value
        self.ignore_value.append('')
        logger.debug('ignore %s' % self.ignore_value)
        self.subparser_name = args.subparser_name
        # 支持 property_list 与 distinct_id_from 共用同一列的特殊需求
        if (not self.is_item) and (not self.is_signup) and (args.property_list != None) and (args.property_list != ""):
            self.skip_cols.remove(args.distinct_id_from)
        # 2. 记下url username password close()的时候要更新元数据
        self.add_cname = False
        if args.add_cname:
            self.add_cname = True
            self.web_url, self.username, self.password = args.web_url, args.username, args.password
            querys = urllib.parse_qs(urllib.urlparse(args.url).query)
            self.project = querys.get('project', ['default'])[0]
        # 3. 初始化csv reader
        self.fd = open(args.filename, 'r', encoding=args.file_encoding)
        self.reader = csv.DictReader(self.fd, **csv_params)
        self.events = set()
        # 4. 获取schema 中间会用fd和reader 所以使用完要reset
        self.column_schema = self.__get_column_schema(skip_identify_list, property_list, args.csv_prefetch_lines)
        self.fd.close()
        self.fd = open(args.filename, 'r', encoding=args.file_encoding)
        self.reader = csv.DictReader(self.fd, **csv_params)

        logger.info('column_schema: %s' % pprint.pformat(self.column_schema, width=200))
        logger.info('events: %s' % self.events)
        logger.info('start import csv from %s' % args.filename)

    @classmethod
    def add_parser(cls, parser):
        '''初始化sub_parser'''
        parser.add_argument('--filename', '-f',
                            help='必填,csv文件名',
                            required=True)
        parser.add_argument('--property_list', '-pl',
                            type=str,
                            help='用逗号分割选取的property, ' \
                                 '举例`-p name,time`将会将name和time两列作为property导入。' \
                                 '如果不填写则表示全部作为property导入',
                            default=None)
        parser.add_argument('--skip_identify', '-i',
                            help='对应的列将不会做自动类型判断，' \
                                 '举例`--skip_identify name,id`将会将name和id不做类型判断，完全作为string导入' \
                                 '如果不填写则表示全部的选中列都会自动做类型判断')
        parser.add_argument('--add_cname', '-ac',
                            action='store_true',
                            help='是否添加中文名，只对event有效. 如果csv的表头是中文，程序会将对应的property名' \
                                 '改为对应的拼音。这时，如果将add_cname选中，会自动再程序的最后把中英文的映' \
                                 '射关系填上去，这样在Ui上看到的对应property就是中文的了.',
                            default=False)
        parser.add_argument('--web_url', '-w',
                            help='如果选择add_cname则必填，web访问的url，单机版类似http://localhost:8007, cloud' \
                                 '版类似http://xxx.cloud.sensorsdata.cn')
        parser.add_argument('--username', '-u',
                            help='如果选择add_cname则必填, web登录用户名')
        parser.add_argument('--password', '-p',
                            help='如果选择add_cname则必填, web登录密码')
        parser.add_argument('--ignore_value',
                            action='append',
                            default=[],
                            help='指定某些值为空，比如指定 `--ignore_value null` 则所有的null都被认为是空值')
        parser.add_argument('--csv_delimiter',
                            type=str,
                            help='csv文件的列分隔符，默认为\',\'，只接受单字符参数，也可以传\\ + ascii的数字，比如\\9表示是\\t',
                            default=',')
        parser.add_argument('--csv_quotechar',
                            type=str,
                            help='csv文件的引用字符，用于指定csv字符串的开始和结尾，默认为\'"\'，只接受单字符参数，也可以传\\ + ascii的数字，比如\\9表示是\\t',
                            default='"')
        parser.add_argument('--csv_prefetch_lines',
                            type=int,
                            help='csv文件预读行数，预读用于判断列的类型，默认为-1，即预读整个文件',
                            default='-1')
        parser.add_argument('--file_encoding',
                            type=str,
                            help='csv文件编码格式，默认为 gbk 编码',
                            default='utf-8')

    def get_total_num(self):
        '''返回总条数'''
        return self.total_num

    def read_records(self):
        '''返回一行'''
        for record in self.reader:
            yield record

    def parse_record(self, record):
        '''解析一行，注意和上面区分 便于异常处理'''
        return record

    def parse_property(self, record):
        properties = {}
        for k in self.column_schema:
            if k not in record:
                continue
            if record[k] in self.ignore_value:
                continue
            properties[self.column_schema[k]['ename']] = format_str(record[k], self.column_schema[k]['type'])
        return properties

    def close(self):
        '''清理方法'''
        self.fd.close()
        super().close()
        if self.add_cname:
            self.__update_meta()
        logger.info('end import csv')

    def __update_meta(self):
        '''更新英文名到中文名的对应关系'''
        # 1.获取token
        auth_response = self.__send_request(
            url='%s/api/auth/login?project=%s' % (self.web_url, self.project),
            content={'username': self.username, 'password': self.password},
            headers={'Content-Type': 'application/json'})
        auth_token = auth_response['token']

        if self.subparser_name.endswith('profile'):
            # 2.取所有profile，得到对应事件profile_id
            for i in range(10):
                if i != 0:
                    time.sleep(30)
                profile_response = self.__send_request(
                    url='%s/api/property/user/properties?show_all=true&cache=false&project=%s' % (
                        self.web_url, self.project),
                    headers={'sensorsdata-token': auth_token})
                profile_dict = {x['name']: x['id'] for x in profile_response}
                remote_ename_set = set(profile_dict.keys())
                local_ename_set = set(column['ename'] for column in self.column_schema.values())
                print(local_ename_set, '==', remote_ename_set)
                if local_ename_set.issubset(remote_ename_set):
                    break

            # 3.更新元数据
            update_meta_request_content = {'property': []}
            for column in self.column_schema.values():
                update_meta_request_content['property'].append({
                    'property_id': profile_dict[column['ename']],
                    'cname': column['cname']})
            update_meta_response = self.__send_request(
                url='%s/api/property/user/properties?project=%s' % (self.web_url, self.project),
                content=update_meta_request_content,
                headers={'sensorsdata-token': auth_token, 'Content-Type': 'application/json'})
            logger.info('successfully update cname for profile.')
        else:
            # self.subparser_name.endswith('event'):
            # 2.取所有events，得到对应事件event_id
            for i in range(10):
                if i != 0:
                    time.sleep(30)
                events_response = self.__send_request(
                    url='%s/api/events/all?cache=false&project=%s' % (self.web_url, self.project),
                    headers={'sensorsdata-token': auth_token})
                # print(events_response_json)
                event_dict = {x['name']: x['id'] for x in events_response}
                event_not_exists = [event for event in self.events if event not in event_dict]
                if not event_not_exists:
                    break
                logger.warning('events%s have not loaded yet. waiting for 0.5 minute.' % event_not_exists)

            # 3.取这个event所有properties，得到各property的id
            for i in range(10):
                all_checked = True
                if i != 0:
                    time.sleep(30)
                event_property_id = {}
                for event in self.events:
                    event_id = event_dict[event]
                    properties_response = self.__send_request(
                        url='%s/api/event/%s/properties?cache=false&project=%s' \
                            % (self.web_url, event_id, self.project),
                        headers={'sensorsdata-token': auth_token})
                    properties_dict = {x['name']: x['id'] for x in properties_response['event']}
                    all_properties = [x['ename'] for x in self.column_schema.values()]
                    property_not_exists = [x for x in all_properties if x not in properties_dict]
                    if property_not_exists:
                        logger.warning('in event %s, properties%s have not loaded yet. waiting for 0.5 minute.' %
                                       (event, property_not_exists))
                        all_checked = False
                        break
                    event_property_id[event] = properties_dict
                if all_checked:
                    break

            # 4.更新元数据
            for event, properties_dict in event_property_id.items():
                event_id = event_dict[event]
                update_meta_request_content = {'event_id': event_id, 'property': []}
                for column in self.column_schema.values():
                    update_meta_request_content['property'].append({
                        'property_id': properties_dict[column['ename']],
                        'cname': column['cname']})
                update_meta_response = self.__send_request(
                    url='%s/api/event/%s/meta?project=%s' % (self.web_url, event_id, self.project),
                    content=update_meta_request_content,
                    headers={'sensorsdata-token': auth_token, 'Content-Type': 'application/json'})
                logger.info('successfully update cname for event %s.' % event)

    def __get_column_schema(self, skip_identify_list, property_list, prefetch_lines):
        # 1. 遍历一遍，得到每一个列的类型，暂时只需要判断是数字还是字符串
        column_type = {}
        total_num = 0
        csv_header = None
        try:
            for record in self.reader:
                # 头的列数比内容少的话 会多个key为None value为一个list的kv
                if None in record:
                    raise Exception('csv error near line %d: content has %d more fields than header' \
                                    % (self.reader.line_num, len(record[None])))
                if self.is_event:
                    event = self.get_event(record)
                    if event not in self.events:
                        self.events.add(event)

                total_num += 1
                if prefetch_lines > 0 and total_num > prefetch_lines:
                    break

                if not csv_header:
                    csv_header = list(record.keys())
                    if property_list:
                        for k in property_list:
                            if k not in csv_header:
                                raise Exception(
                                    'invalid param property_list: cannot find column "%s" in csv header %s' % (
                                        k, csv_header))
                    else:
                        property_list = csv_header

                for k in property_list:
                    # 将用于选择event/distinc_id/time的列去掉
                    if k in self.skip_cols:
                        continue
                    # 用户指定不做自动检查的列
                    if k in skip_identify_list:
                        column_type[k] = 'string'
                        continue
                    column = record[k]
                    # 内容的列数比头少的话 对应key的value为none
                    if column is None:
                        raise Exception('csv error near line %d: no value for field %s' \
                                        % (self.reader.line_num, k))
                    # 空字符串跳过
                    if column in self.ignore_value:
                        continue
                    # 只要有一个是字符串就全当字符串用
                    guess_type = guess_str_type(column)
                    if guess_type == 'string':
                        column_type[k] = 'string'
                    elif k not in column_type:
                        column_type[k] = guess_type
        except csv.Error as e:
            logger.warning('csv error near line %d' % self.reader.line_num)
            raise e
        self.total_num = -1 if prefetch_lines > 0 else total_num
        # 2. 增加ename
        schema = {k: {'cname': k, 'ename': self.__get_ename(k), 'type': column_type[k]} for k in column_type}
        # 3. 检查参数里面指定的列是否存在
        for k in skip_identify_list:
            if k not in csv_header:
                raise Exception(
                    'invalid param skip_identify: cannot find column "%s" in csv header %s' % (k, csv_header))
        return schema

    def __get_ename(self, cname):
        '''
        从中文转拼音
        '''
        if CsvFormatter.ename_pattern.match(cname):
            return cname
        first_ename = pypinyin.slug(cname, separator='', errors='default')
        first_ename = first_ename.lower()
        second_ename = ''
        for ch in first_ename:
            if ch in 'abcdefghijklmnopqrstuvwxyz1234567890':
                second_ename += ch
        second_ename = second_ename[0:90]
        return second_ename

    def __send_request(self, url, content=None, headers={}):
        '''
        发送get请求(args同urllib2.Request)
        '''
        for i in range(3):
            try:
                if i != 0:
                    time.sleep(2)
                request_content = json.dumps(content).encode() if content else None
                request = urllib2.Request(url=url, data=request_content, headers=headers)
                response = urllib2.urlopen(request)
                response_content = json.loads(response.read().decode('utf-8'))
                logger.debug('request %s succeed' % url)
                logger.debug('content:\n%s\nheaders\n%s\nresponse\n%s' % (content, headers, response_content))
                return response_content
            except Exception as e:
                logger.warning(e)
                logger.warning('failed to request %s for %d times' % (url, i))
                logger.debug(traceback.format_exc())
        else:
            raise Exception('failed to request %s!' % url)


class NginxFormatter(BaseFormatter):
    '''将Nginx日志导入
注意会做一些url解析工作:
    1. 将$request解析，__request_method表示方法(GET), __request_path表示请求的path(去除参数),
       __request_query表示参数，__request_param_xx表示参数里面的xx。
    2. 将--url_fields指定的列认为是url并做解析，解析后会生成__<字段名>_<解析内容>这样命名的property,
       解析内容包括netloc, path, query, param_<参数明>。举例对于$my_url字段值为
       "http://www.abc.com/path/to/mine?k1=v1&k2=2", 会解析为
       {
           "__my_url_netloc": "www.abc.com",
           "__my_url_path": "/path/to/mine",
           "__my_url_query": "k1=v1&k2=v",
           "__my_url_param_k1": "v1",
           "__my_url_param_k2": 2
       }

举例:
    1. format_importer.py nginx_event -l 'http://localhost:8006/sa' -ef '__http_referer_path' -df
       __request_param_cookieId -td '2014-08-01 12:00:00' -f access.log
       -F '$remote_addr - $remote_user [$time_local] "$request" $status +++$request_body+++ "$http_referer"'
       将access_log中所有列作为properties导入本地的私有部署版本，其中每行是一个事件，http_refer解析后
       的path对应的列为事件名，request解析后参数中的cookieId作为用户id, 时间全部为2014-08-01 12:00:00
    2. format_importer.py nginx_event -l 'http://localhost:8006/sa' -ed my_event -df
       __request_param_cookieId -tf time_local -fm "%d/%b/%Y:%H:%M:%S %z"
       -F '$remote_addr - $remote_user [$time_local] "$request" $status +++$request_body+++ "$my_url"'
       -pl 'status,__my_url_netloc' -uf my_url -fp '.*\.gif' -fp '.*\.png'
       将access_log中(status, http_refer解析后的netloc)作为properties导入本地的私有部署版本，
       过滤所有对gif,png的请求。对应事件名全部为my_event, 每行是一个事件, request解析后参数中的
       cookieId为distinct_id, time_local对应的列为time(格式类似22/Oct/2015:17:56:27 +0800),
       并且将my_url字段作为url解析。
    3. format_importer.py nginx_profile -l 'http://localhost:8006/sa' -df __request_param_cookieId -f access.log
       -F '$remote_addr - $remote_user [$time_local] "$request" $status +++$request_body+++ "$http_referer"
       将access_log中所有列作为用户属性导入本地的私有部署版本，其中每行是一个用户, request解析后参
       数中的cookieId作为用户id.
    4. format_importer.py nginx_event @./conf/nginx_event.conf
       也可以修改conf/nginx_event.conf和conf/nginx_profile.conf来填写所有必要参数
    '''

    def __init__(self, args):
        '''初始化方法'''
        super().__init__(args, args.filename)
        # 规范化
        property_list = args.property_list.split(',')
        if args.property_list_cnames:
            property_list_cnames = args.property_list_cnames.split(',')
            if len(property_list_cnames) != len(property_list):
                raise Exception(
                    'name umatch! property_list contains %d properties, property_list_cnames contains %d names!' \
                    % (len(property_list), len(property_list_cnames)))
            self.property_cname_map = dict(zip(property_list, property_list_cnames))
        else:
            self.property_cname_map = {}
        skip_identify_list = args.skip_identify.split(',') if args.skip_identify else []
        self.url_fields = args.url_fields.split(',')
        self.filter_path_patterns = [re.compile(x) for x in args.filter_path]
        self.ip_from = args.ip_from
        self.ignore_value = args.ignore_value
        self.ignore_value.append('')
        logger.debug('ignore %s' % self.ignore_value)
        # 支持 property_list 与 distinct_id_from 共用同一列的特殊需求
        if (not self.is_item) and (not self.is_signup) and (args.property_list != None) and (args.property_list != ""):
            self.skip_cols.remove(args.distinct_id_from)
        # 生成columns
        self.columns, self.log_format_pattern = self.__compile_log_format(args.log_format)
        self.nginx_fd = open(args.filename, 'r')
        # 判断type 需要预读一段数据 因此判断完需要重置句柄
        self.column_type = self.__get_column_type(skip_identify_list, property_list)
        self.nginx_fd.close()
        self.nginx_fd = open(args.filename, 'r')

        logger.info('start import nginx, filename = %s, log_format = %s' % (args.filename, args.log_format))
        logger.info('columns = %s' % self.columns)
        logger.info('column_type: %s' % pprint.pformat(self.column_type, width=200))
        logger.info('property_cname_map: %s' % pprint.pformat(self.property_cname_map, width=200))

    @classmethod
    def add_parser(cls, parser):
        '''初始化sub_parser'''
        parser.add_argument('--filename', '-f',
                            help='必填,nginx日志文件路径',
                            required=True)
        parser.add_argument('--log_format', '-F',
                            help='必填,nginx日志配置，类似\'"$remote_addr" "$time_local" "$http_refer" "$status"\'',
                            required=True)
        parser.add_argument('--property_list', '-pl',
                            type=str,
                            help='必填,用逗号分割选取的property, ' \
                                 '举例`-p http_refer,status`将会将http_refer和status两列作为property导入。',
                            required=True)
        parser.add_argument('--property_list_cnames', '-pc',
                            type=str,
                            help='用逗号分割property的对应名称, 需要和--property_list一一对应',
                            default=None)
        parser.add_argument('--skip_identify', '-i',
                            help='对应的列将不会做自动类型判断，' \
                                 '举例`--skip_identify request_user,status`将会将request_user,status不做类型判断，'
                                 '完全作为string导入。如果不填写则表示全部的选中列都会自动做类型判断')
        parser.add_argument('--url_fields', '-uf',
                            help='对应的列将作为url解析，用逗号分割。解析后会生成__<字段名>' \
                                 '_<解析内容>这样命名的property, 解析内容包括netloc, path, query, param_<参数明>' \
                                 '。举例对于$my_url字段值为"http://www.abc.com/path/to/mine?k1=v1&k2=2", ' \
                                 '会解析为{"__my_url_netloc": "www.abc.com", "__my_url_path": "/path/to/mine", ' \
                                 '"__my_url_query": "k1=v1&k2=v", "__my_url_param_k1": "v1", "__my_url_param_k2": 2}' \
                                 '注意可以再property_list配置这些字段。默认是"http_referer"',
                            default='http_referer')
        parser.add_argument('--filter_path', '-fp',
                            help='过滤对应的path，可多选。这里的path取的是$request的path.支持正则. 举例 ' \
                                 '-fp \'.*\.gif\' -fp \'/index\.html\' 将过滤对gif的请求和index的请求过滤掉',
                            action='append',
                            default=[])
        parser.add_argument('--ip_from', '-if',
                            help='哪个字段作为ip, 如果指定，则每条数据对应的ip为对应字段的值, 默认是$remote_addr',
                            default='remote_addr')
        parser.add_argument('--ignore_value',
                            action='append',
                            default=[],
                            help='指定某些值为空，比如指定 `--ignore_value null` 则所有的null都被认为是空值')

    def get_total_num(self):
        '''返回总条数'''
        return self.total_num

    def read_records(self):
        '''返回一行'''
        return self.__parse_nginx_log()

    def parse_record(self, record):
        '''解析一行，注意和上面区分 便于异常处理'''
        return record

    def parse_property(self, record):
        '''解析properties'''
        properties = {}
        for column, column_type in self.column_type.items():
            if column not in record:
                continue
            # 空字符串跳过
            if record[column] in self.ignore_value:
                continue
            value = format_str(record[column], column_type)
            if self.property_cname_map:
                properties[self.property_cname_map[column]] = value
            else:
                properties[column] = value
        if self.is_event:
            properties['$ip'] = record[self.ip_from]
        return properties

    def close(self):
        '''清理方法'''
        self.nginx_fd.close()
        super().close()
        logger.info('end import nginx')

    def __compile_log_format(self, log_format_str):
        '''将Nginx log format转化为正则'''
        variable_pattern = re.compile(r'\$[a-zA-Z0-9_]*')
        columns_with_dolla = variable_pattern.findall(log_format_str)
        columns = [x[1:] for x in columns_with_dolla]
        log_format_pattern = log_format_str
        # 1. metachars
        metachars = '\.^*+?{}[]|()'
        for char in metachars:
            log_format_pattern = log_format_pattern.replace(char, '\\%s' % char)
        # 2. 替换$xxx
        for s in columns_with_dolla:
            log_format_pattern = log_format_pattern.replace(s, '(.*)', 1)
        # 3. 整行匹配
        log_format_pattern = '%s$' % log_format_pattern
        logger.info('log_format: %s' % log_format_str)
        logger.info('re pattern: %s' % log_format_pattern)
        logger.info('columns: %s' % columns)
        return columns, re.compile(r'%s' % log_format_pattern)

    def __parse_nginx_log(self):
        '''按照pattern解析nginx log'''
        for line in self.nginx_fd.readlines():
            line = line.rstrip('\n')

            # 1. 正则解析Nginx日志
            m = self.log_format_pattern.match(line)
            if not m:
                logger.warning('invalid log line')
                logger.warning(line)
                raise Exception('log line not matched')
            values = m.groups()
            record = dict([(x, y) for x, y in zip(self.columns, values) if y])

            # 2. 对$request解析
            if 'request' in record:
                parse_result = self.__parse_request(record['request'])
                record.update(parse_result)

            # 3. 过滤规则
            is_filter = False
            for p in self.filter_path_patterns:
                if p.match(record['__request_path']):
                    logger.debug('filter %s' % line)
                    is_filter = True
                    break
            if is_filter:
                continue

            # 4. 对内建的解析url
            for url_name in self.url_fields:
                if url_name not in record:
                    continue
                parse_result = self.__parse_url(record[url_name])
                for k, v in parse_result.items():
                    if v:
                        record['__%s_%s' % (url_name, k)] = v

            yield record

    def __get_column_type(self, skip_identify_list, property_list):
        # 1. 遍历一遍，得到每一个列的类型，暂时只需要判断是数字还是字符串
        column_type = {}
        self.total_num = 0
        for record in self.__parse_nginx_log():
            self.total_num += 1
            # property_list如果用户没有指定 则认为全部导入
            if not property_list:
                property_list = record.keys()
            for k in property_list:
                if k not in record:
                    continue
                # 将用于选择event/distinc_id/time的列去掉
                if k in self.skip_cols:
                    continue
                # 用户指定不做自动检查的列
                if k in skip_identify_list:
                    column_type[k] = 'string'
                    continue
                column = record[k]
                if column in self.ignore_value:
                    continue
                # 只要有一个是字符串就全当字符串用
                guess_type = guess_str_type(column)
                if guess_type == 'string':
                    column_type[k] = 'string'
                elif k not in column_type:
                    column_type[k] = guess_type
        return column_type

    def __parse_url(self, url):
        """解析url"""
        parse_result = urllib.urlparse(urllib.unquote(url))
        ret = {
            'netloc': parse_result.netloc,
            'path': parse_result.path,
            'query': parse_result.query,
        }
        params = urllib.parse_qs(parse_result.query)
        for k, v in params.items():
            ret['param_%s' % k] = v[0]
        return ret

    def __parse_request(self, request):
        """解析request:GET /behavior/access/?p=click&uid="""
        fields = request.split(' ')
        ret = {'__request_method': fields[0]}
        rest = ' '.join(fields[1:])
        parse_result = urllib.urlparse(rest)
        ret['__request_path'] = parse_result.path
        ret['__request_query'] = parse_result.query
        params = urllib.parse_qs(parse_result.query)
        for k, v in params.items():
            ret['__request_param_%s' % k] = v[0]
        return ret


class SQLFormatter(BaseFormatter):
    """mysql/oracle/hive等访问的基类 因为框架差不多 抽象了下相关代码"""
    # 需要指定哪些类型可以作为bool备选
    bool_property_types = []
    # 字符串说明数据库类型
    db_type = ''
    # 大小写敏感默认参数, 默认是false 但是mysql是true 主要为了和之前兼容
    default_is_case_sensitive = False

    def __init__(self, args):
        '''初始化方法'''
        self.conn = self.create_connection(args)
        if args.sql:
            self.sql = args.sql
        else:
            with open(args.filename) as f:
                self.sql = f.read()
        # 特殊处理 如果大小写敏感需要先将相关参数改成统一大写 再调用基类的init
        if args.case_sensitive:
            self.column_wrapper = lambda x: x
        else:
            self.column_wrapper = lambda x: x.upper()
        for k in ['distinct_id_from', 'timestamp_from', 'event_from', 'item_type', 'item_id']:
            if hasattr(args, k) and getattr(args, k):
                setattr(args, k, self.column_wrapper(getattr(args, k)))
        super().__init__(args, self.sql.replace('\t', ' ').replace('\n', ' '))
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.sql)
        self.total_num = self.cursor.rowcount
        logger.info('start importing from %s, sql=%s' % (self.__class__.db_type, self.sql))
        self.columns = [self.column_wrapper(x[0]) for x in self.cursor.description]
        if self.__class__.bool_property_types:
            self.bool_property_list = [self.column_wrapper(x) for x in args.bool_property_list.split(',')] \
                if args.bool_property_list else []
            # 检查bool_property_list的参数是否合法 包括类型是否匹配
            self.type_dict = {self.column_wrapper(x[0]): x[1] for x in self.cursor.description}
            for p in self.bool_property_list:
                if p not in self.type_dict:
                    raise Exception('invalid param bool_property_list, property[%s] not found in %s' % (
                        p, list(self.type_dict.keys())))
                if self.type_dict[p] not in self.__class__.bool_property_types:
                    raise Exception('invalid param bool_property_list, property[%s] is not in %s' % (
                        p, self.__class__.bool_property_types))

    @classmethod
    @abc.abstractmethod
    def create_connection(cls, args):
        """构建一个connection"""
        pass

    @classmethod
    @abc.abstractmethod
    def add_db_parser(cls, parser):
        """初始化sub parser 数据库相关的参数"""
        pass

    @classmethod
    def add_parser(cls, parser):
        '''初始化sub_parser'''
        # sql必须要么传入整个sql 要么指定一个sql文件
        sql_group = parser.add_mutually_exclusive_group(required=True)
        sql_group.add_argument('--sql', '-q',
                               help='和filename选一个必填，查询语句，建议加order by等方式保证多次查询结果顺序一致。')
        sql_group.add_argument('--filename', '-f',
                               help='和sql选一个必填，查询语句所在的文件，建议加order by等方式保证多次查询结果顺序一致。')
        parser.add_argument('--case_sensitive',
                            help='可填,true/false,是否是大小写敏感，注意如果大小写不敏感会全部转化为大写, 默认为%s' % cls.default_is_case_sensitive,
                            default=cls.default_is_case_sensitive,
                            type=bool,
                            required=False)
        if cls.bool_property_types:
            parser.add_argument('--bool_property_list', '-bp',
                                help='逗号分割的bool类型属性列表，会将对应的属性值为1的转化为true，0转化为false')
        cls.add_db_parser(parser)

    def parse_record_value(self, key, value):
        """读取的数据根据数据库类型可能会做一些简单转化 比如把mysql的decimal该成float"""
        if self.__class__.bool_property_types and key in self.bool_property_list:
            if value == 1:
                return True
            elif value == 0:
                return False
            else:
                raise Exception('invalid %s value %d(bool property should be either 0 or 1' % (key, value))
        return value

    def get_total_num(self):
        '''返回总条数'''
        return self.total_num

    def read_records(self):
        '''返回一行'''
        while True:
            row = self.cursor.fetchone()
            if not row or len(row) == row.count(None):
                break
            yield row

    def parse_record(self, row):
        '''解析一行，注意和上面区分 便于异常处理'''
        record = {}
        for x, y in zip(self.columns, row):
            # 去除空列
            value = self.parse_record_value(x, y)
            if value is None:
                continue
            record[x] = value
        return record

    def parse_property(self, record):
        # '''解析properties'''
        return {k: v for k, v in record.items() if k not in self.skip_cols}

    def close(self):
        '''清理方法'''
        self.cursor.close()
        self.conn.close()
        super().close()
        logger.info('end import from %s.' % self.__class__.db_type)


class MysqlFormatter(SQLFormatter):
    """提供sql，将mysql的数据导入
使用举例:
    1. format_importer.py mysql_event -l 'http://localhost:8006/sa' -ef event -df user -td '2014-08-01 12:00:00'
       -u root -p passwd -i localhost -P 1234 -d test_db
       -q 'select event, user, col from event where d = '2014-08-01' order by id'
       查询mysql中event表，将col对应的列作为properties导入本地的私有部署版本，其中每行是一个事件，
       event字段对应的是事件名, user字段对应的是distinct_id, 时间全部为2014-08-01 12:00:00
    2. format_importer.py mysql_event -l 'http://localhost:8006/sa' -ed my_event -df user -tf time -fm '%Y%m%d%H%M%S'
       -q 'select user,time,col1,col2,col3 from event where d = '2014-08-01' order by id'
       查询mysql中event表，将(col1, col2, col3)作为properties导入本地的私有部署版本，
       对应事件名全部为my_event, 每行是一个事件，user对应的列为distinct_id,
       time对应的列为time(格式类似20150130125959)
    3. format_importer.py mysql_profile -l 'http://localhost:8006/sa' -df user
       -u root -p passwd -i localhost -P 1234 -d test_db
       -q 'select user, col from profile where d = '2014-08-01' order by id'
       查询mysql中profile表，将col对应的列作为用户属性导入本地的私有部署版本，其中每行是一个用户,
       user字段对应的是distinct_id
    4. format_importer.py mysql_event @./conf/mysql_event.conf
       也可以修改conf/mysql_event.conf和conf/mysql_profile.conf来填写所有必要参数
    """
    db_type = 'mysql'
    # 具体类型在init阶段获取 此处只表示需要指定bool类型
    bool_property_types = ['xxx']
    # 默认大小写敏感
    default_is_case_sensitive = True

    def __init__(self, args):
        '''初始化方法'''
        try:
            import pymysql
        except ImportError as e:
            logger.error('pymysql not installed! please install pymysql by "python3 -m pip install PyMySQL --upgrade"')
            raise e
        MysqlFormatter.bool_property_types = [pymysql.FIELD_TYPE.TINY, pymysql.FIELD_TYPE.SHORT,
                                              pymysql.FIELD_TYPE.LONG, pymysql.FIELD_TYPE.LONGLONG,
                                              pymysql.FIELD_TYPE.INT24]
        super().__init__(args)

    @classmethod
    def create_connection(cls, args):
        import pymysql
        return pymysql.connect(
            host=args.host,
            port=args.port,
            user=args.user,
            charset='utf8',
            passwd=args.password,
            db=args.db)

    @classmethod
    def add_db_parser(cls, parser):
        parser.add_argument('--user', '-u',
                            help='必填，mysql的username',
                            required=True)
        parser.add_argument('--password', '-p',
                            help='必填，mysql的password',
                            required=True)
        parser.add_argument('--host', '-i',
                            help='必填，mysql的地址',
                            required=True)
        parser.add_argument('--port', '-P',
                            help='必填，mysql的端口号',
                            type=int,
                            required=True)
        parser.add_argument('--db', '-d',
                            help='必填, mysql对应的db名',
                            required=True)

    def parse_record_value(self, key, value):
        # 把date类型转化成datetime
        if type(value) == datetime.date:
            return datetime.datetime.combine(value, datetime.datetime.min.time())
        elif type(value) == decimal.Decimal:
            return float(value)
        else:
            return super().parse_record_value(key, value)


class JsonFormatter(BaseFormatter):
    """将json格式日志全部导入，日志格式参考https://www.sensorsdata.cn/manual/data_schema.html
使用举例
1. format_importer.py json -p ./test.log -l 'http://localhost:8006/sa'
将test.log里面的数据导入本地的私有部署版本，test.log是一个日志文件，每行是一个符合我们要求的json
2. format_importer.py json -p ./log_dir -l 'http://localhost:8006/sa'
将log_dir目录下所有文件导入本地的私有部署版本，每个文件都是日志文件，每行是一个符合我们要求的json
    """

    def __init__(self, args):
        '''初始化方法
注意没有调用super() 这是因为读取json文件不需要指定distinct_from, event_from等等
而且也不区分event/profile
只需要标记lib相关信息即可'''
        self.args = args
        # 记录导入信息的
        self.default_properties = {
            '$lib': 'FormatImporter',
            '$lib_version': __version__,
            '$lib_method': 'tools',
            '$lib_detail': ('Json##%s' % args.path)[:100],
        }
        # 获取文件列表 可能是一个文件 也可能是多个
        self.file_list = []
        if os.path.isfile(args.path):
            self.file_list.append(args.path)
        elif os.path.isdir(args.path):
            for f in os.listdir(args.path):
                abs_filename = os.path.join(args.path, f)
                if not os.path.isfile(abs_filename):
                    raise Exception('invalid path %s: %s is not a file' % (args.path, f))
                self.file_list.append(abs_filename)
        else:
            raise Exception('invalid path %s cannot find file or directory' % (args.path))
        self.file_list = sorted(self.file_list)
        logger.info('total %d json files' % len(self.file_list))
        logger.debug(self.file_list)
        # 预读取一遍 获取行数
        self.total_num = 0
        for f in self.file_list:
            n = 0
            with open(f) as fd:
                for l in fd:
                    n += 1
            logger.debug('%d lines in %s' % (n, f))
            self.total_num += n

    def set_consumer(self, consumer):
        '''只是简单set consumer 不需要初始化sa 因为只调用了静态方法'''
        self.consumer = consumer

    @classmethod
    def add_parser(cls, parser):
        '''初始化sub_parser'''
        parser.add_argument('--path', '-p',
                            help='必填,日志的文件/目录路径',
                            required=True)

    def get_total_num(self):
        '''返回总条数'''
        return self.total_num

    def read_records(self):
        '''返回一行'''
        for f in self.file_list:
            logger.info('start reading from file %s' % f)
            with open(f) as fd:
                for l in fd:
                    yield l
            logger.info('end reading from file %s' % f)

    def parse_record(self, record):
        '''解析一行，注意和上面区分 便于异常处理'''
        return record

    def send(self, l):
        record = json.loads(l)
        '''直接调用雨晗的那个接口 注意需要加下lib和project 以及timefree'''
        if record['type'].startswith('item'):
            record['time'] = int(time.time() * 1000)
            data = sensorsanalytics.SensorsAnalytics._normalize_item_data(record)
            self.consumer.send(sensorsanalytics.SensorsAnalytics._json_dumps(data))
        else:
            record['time_free'] = True
            if 'lib' not in record:
                record['lib'] = self.default_properties
            if 'project' not in record and self.args.project:
                record['project'] = self.args.project
            # 坑坑：雨晗的代码里面即使是profile也需要有time 所以这里加上个time 反正不生效
            if record['type'].startswith('profile_'):
                record['time'] = int(time.time() * 1000)
            data = sensorsanalytics.SensorsAnalytics._normalize_data(record)
            self.consumer.send(sensorsanalytics.SensorsAnalytics._json_dumps(data))

    # def send_item(self,l):
    # record = json.loads(l)
    # data = sensorsanalytics.SensorsAnalytics._normalize_item_data(record)
    # self.consumer.send(sensorsanalytics.SensorsAnalytics._json_dumps(data))

    def close(self):
        self.consumer.close()


class OracleFormatter(SQLFormatter):
    """提供sql，将oracle的数据导入
使用举例:
    1. format_importer.py oracle_event -l 'http://localhost:8006/sa' -ef event -df user -td '2014-08-01 12:00:00'
       -u root -p passwd -dsn '127.0.0.1/orcl'
       -q 'select event, user, col from event where d = '2014-08-01' order by id'
       查询oracle中event表，将col对应的列作为properties导入本地的私有部署版本，其中每行是一个事件，
       event字段对应的是事件名, user字段对应的是distinct_id, 时间全部为2014-08-01 12:00:00
    2. format_importer.py oracle_profile @./conf/oracle_profile.conf
       也可以修改conf/oracle_event.conf和conf/oracle_profile.conf来填写所有必要参数
    """
    db_type = 'oracle'
    # 具体类型在init阶段获取 此处只表示需要指定bool类型
    bool_property_types = ['xxx']
    # 默认大小写不敏感
    default_is_case_sensitive = False

    def __init__(self, args):
        """初始化方法"""
        try:
            import cx_Oracle
        except ImportError as e:
            logger.error(
                'cx_Oracle not installed! please install cx_Oracle by "python3 -m pip install cx_Oracle --upgrade"')
            raise e
        OracleFormatter.bool_property_types = [cx_Oracle.NUMBER]
        super().__init__(args)

    @classmethod
    def create_connection(cls, args):
        import cx_Oracle
        if args.nls_lang != 'utf-8':
            os.environ['NLS_LANG'] = args.nls_lang
            return cx_Oracle.connect(
                user=args.user,
                password=args.password,
                dsn=args.dsn)
        else:
            return cx_Oracle.connect(
                user=args.user,
                password=args.password,
                dsn=args.dsn,
                encoding='utf8')

    def get_total_num(self):
        """oracle的接口无法返回具体查询条数"""
        return -1

    @classmethod
    def add_db_parser(cls, parser):
        """初始化sub_parser"""
        parser.add_argument('--user', '-u',
                            help='必填，oracle的username',
                            required=True)
        parser.add_argument('--password', '-p',
                            help='必填，oracle的password',
                            required=True)
        parser.add_argument('--dsn', '-dsn',
                            help='必填，oracle的dsn',
                            required=True)
        parser.add_argument('--nls_lang',
                            type=str,
                            help='数据库字符集，默认 utf-8',
                            default='utf-8')

    def parse_record_value(self, key, value):
        # 把clob类型转化成str
        import cx_Oracle
        if type(value) == cx_Oracle.LOB:
            return value.read()
        else:
            return super().parse_record_value(key, value)


#######
#
# main需要的
#
######
def main():

    args = parse_args()
    # 单个文件最大1m 最多10个文件
    fa = logging.handlers.RotatingFileHandler(log_file, 'a', 1024 * 1024, 10)
    fa.setLevel(args.log_level)
    fa.setFormatter(formater)
    logger.addHandler(fa)

    logger.debug('args: %s' % pprint.pformat(vars(args)))

    formatter_name = '%sFormatter' % args.subparser_name.split('_')[0].title()
    formatter = globals()[formatter_name](args)

    if args.output_file:
        logger.info('logging file to %s only', args.output_file)
        consumer = sensorsanalytics.LoggingConsumer(args.output_file)
    else:
        check_url(args.url)
        if args.debug:
            logger.info('running debug mode')
            consumer = sensorsanalytics.DebugConsumer(args.url, False, 10000)
        else:
            logger.info('sending msg to %s directly' % args.url)
            consumer = sensorsanalytics.BatchConsumer(args.url)
    formatter.set_consumer(consumer)

    skip_lines_cnt_down = args.skip_cnt
    total = formatter.get_total_num()
    if total == 0:
        raise Exception('cannot find valid line!')
    counter = {'total_write': 0, 'total_read': 0, 'error': 0, 'skip': args.skip_cnt}
    error = False
    if total > 0:
        counter['total'] = total
        progress_interval = 10000 if total < 10000 * 20 else (total / 100)
    else:
        progress_interval = 10000
    for record in formatter.read_records():
        try:
            if counter['total_read'] % progress_interval == 0:
                if total > 0:
                    percent = counter['total_read'] * 100.0 / counter['total']
                    logger.info('progress %.2f%% %s' % (percent, counter))
                else:
                    logger.info('progress %s' % counter)
            counter['total_read'] += 1
            if skip_lines_cnt_down > 0:
                skip_lines_cnt_down -= 1
                continue
            record = formatter.parse_record(record)
            formatter.send(record)
            counter['total_write'] += 1
        except Exception as e:
            counter['error'] += 1
            logger.warning('failed to parse line %d' % counter['total_read'])
            logger.warning(traceback.format_exc())
            logger.warning(e)
            if args.quit_on_error:
                error = True
                break

    formatter.close()

    if error:
        logger.error('failed to import, please fix it and run with[--skip_cnt %d] again!' %
                     counter['total_write'])
        return 1
    else:
        logger.info('counter = %s.' % counter)
        if args.debug:
            logger.info('--debug 参数时不会真正导入数据')
        else:
            logger.info('数据已发送到神策分析，请查看埋点管理，确认数据是否校验通过')
        return 0


if __name__ == '__main__':
    sys.exit(main())
