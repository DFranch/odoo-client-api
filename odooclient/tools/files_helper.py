# -*- coding: utf-8 -*-
import io
import os
import csv
import xlrd
import pprint
import base64
import logging
from urllib.parse import urlparse
import requests
import itertools
import traceback
import importlib
import io
import datetime

FORMAT = "%(asctime)-15s - %(url)s - %(user)s :: "
#logging.basicConfig(format=FORMAT, level=logging.DEBUG)
_logger = logging.getLogger("OdooClient ")

DEFAULT_IMAGE_TIMEOUT = 100
DEFAULT_IMAGE_MAXBYTES = 25 * 1024 * 1024
DEFAULT_IMAGE_CHUNK_SIZE = 32768

pp = pprint.PrettyPrinter(indent=4)

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def read_csv_data(path):
    """
    Reads CSV from given path and Return list of dict with Mapping
    """
    data = csv.reader(open(path, encoding='ISO-8859-1'))
    # Read the column names from the first line of the file
    fields = next(data)
    data_lines = []
    for row in data:
        items = dict(zip(fields, row))
        data_lines.append(items)
    return data_lines

def get_field_mapping(values, mapping):
    """
    Final Field Mapper for the Preparing Data for the Import Data
    use for def load in orm
    """
    fields=[]
    data_lst = []
    for key, val in mapping.items():
        if key not in fields and values:
            fields.append(key)
            value = values.get(val)
            if value == None:
                value = ''
            data_lst.append(value)
    return fields, data_lst

def read_xls(fname):
    """ Read file content, using xlrd lib """
    return xlrd.open_workbook(fname)

def read_filemap(walk_dir):
    file_map = dict([
        (filename, os.path.join(root, filename))
            for root, subdirs, files in os.walk(walk_dir)
                for filename in files
    ])
    print ('Found {:6} files in dir "{}" .'.format(len(file_map), walk_dir))
    return file_map

def cache_model_data(conn, model, key_field=None, value_field=None):
    """
    This help in caching model in dict in running script so
    for getting some id for relations, wea are not forced to query db
    """
    if key_field == None:
        key_field = 'name'
    if value_field == None:
        value_field = 'id'
    record_ids = {}
    for record in conn.SearchRead(model, [],fields=[ key_field, value_field ]):
        record_ids.update({record[key_field]: record[value_field]})
    print ('Cached {:6} records of model `{}`.'.format(len(record_ids), model))
    return record_ids