#!/usr/bin/env python3
#coding: utf8
#  vim: set sw=4

import yaml
import argparse
import os, sys, time
from itertools import islice
from datetime import datetime, timedelta
import glob
from code.helper import *



def cut_line_1(fin,tmp_file):
    with open(fin, 'r') as f0:
        data = f0.read().splitlines(True)
    with open(tmp_file, 'w') as fout:
        fout.writelines(data[1:])

def lookup_yaml(yaml_data,keys,node):
    value = yaml_data
    for key in keys.split('.'):
        if isinstance(value, dict):
            if not key in value:
                logv('key %s does not exist for node: %s' % (key, node))
                value = "__unknown__"
            else:
                value = value[key]
        else:
            logv('key %s cannot be read for node %s' % (key,node))
            value = "__unknown__"
            break
    return value

def generate_yaml(path, filehandle, node):
    conf_file = os.path.dirname(os.path.realpath(__file__)) + '/../conf/conf.yaml'
    if not os.path.isfile(conf_file):
        print('ERROR: conf file does not exist: %s' % conf_file)
        sys.exit(1)
    else:
        with open(conf_file, 'r') as ymlconf:
            cfg = yaml.load(ymlconf, Loader=yaml.SafeLoader)

    tmp_file = cfg['tmp_file']
    tags_list = cfg['tags_list']
    keys_dict = cfg['yamlstruct']['keys']

    if not os.path.isfile(path):
        print('ERROR: file does not exist: %s' % path)
        sys.exit(1)
    else:
        cut_line_1(path,tmp_file)
        f = open(tmp_file, 'r')
        yaml_data = yaml.load(f, Loader=yaml.SafeLoader )
        tags = []

        try:
            sub_dict = {}
            for key in keys_dict:
                sub_dict[key] = lookup_yaml(yaml_data,keys_dict[key],node)

            sub_dict['tags'] = []
            for tag in tags_list:
                if tag in keys_dict:
                    sub_dict['tags'].append(sub_dict[tag])
                else:
                    logv('tag %s is not part of your keys' % tag)

            d = {lookup_yaml(yaml_data,cfg['yamlstruct']['node_name'],node):sub_dict}

            yaml.dump(d, filehandle, default_flow_style=False)
        except TypeError:
            log('ERROR: TypeError caught, skipping node %s.' % node)

        f.close()
