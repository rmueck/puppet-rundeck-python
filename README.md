# Puppet Rundeck

Feed Rundeck with Puppet nodes.

This is a fork from https://github.com/virtual-expo/puppet-rundeck-python

I had to slightly modify the original code, because it did not produce the expected output for *Rundeck*:

- Change `parameters` to `values` in config
- Change default input directory to `/opt/puppetlabs/server/data/puppetserver/yaml/facts`
- Adding the `Loader=yaml.SafeLoader` to all `yaml.load` statements (see https://github.com/yaml/pyyaml/wiki/PyYAML-yaml.load(input)-Deprecation)


This Python script reads into the Puppet Master filesystem and produces a yaml file containing up-to-date nodes information. The nodes description is based on Puppet facts and reads from the yaml node reports written by puppet. The output file respects [Rundeck resource yaml format](http://rundeck.org/docs/man5/resource-yaml.html). Facts (custom or not) can be added at will, and are then available in Rundeck Node Filter.

The final yaml file should be exposed to an internal address, used as a URL Source in Rundeck Project Nodes configuration.


## Requirement
* Python 3

## Usage
This script should run on the Puppet Master and have read access to puppet directories.

```bash
cp conf/conf_example.yaml conf/conf.yaml
./puppet_to_rundeck.py [OPTIONS]
```

### Options

Name | Description | Default
--- | --- | ---
`-o, --outfile` | **Required:** output yaml file |
`-i, --inputdir` | input directory containg puppet nodes yaml files | `/opt/puppetlabs/server/data/puppetserver/yaml/facts`
`-m, --maxage` | max age of input node files (days) | 7


### Configuration

The file `conf/conf.yaml` should be copied from `conf/conf_example.yaml` and adapted. Sections:

* `tmp_file`: the temporary file where the script will write before replacing the output file with its new version
* `yamlstruct`: the yaml block describing each node. It should be formatted in this way:
```yaml
yamlstruct:
  node_name: yournodename
  keys:
    key1: value1
    key2: value2
    key3: value3
```
where `yournodename` is the title of your yaml block. The `node_name` entry is mandatory.
`keyN` is an optionnal entry, like a fact you want to access via Rundeck Node Filter.
* `tags_list`: is a list of tags, which are used in Rundeck for node filtering. The tag list is a subset of {key1, key2,...,keyN}.

If you need to add a few nodes **not** managed by Puppet, you can describe them in the file `conf/other_nodes.yaml`, following the example file `conf/other_nodes_example.yaml`.


### Example

Assuming your configuration file `conf/conf.yaml` is the following:
```yaml
---
tmp_file: /tmp/tmpfile.yaml
tags_list:
  - osFamily
  - osVersion
  - virtual
  - customfact

yamlstruct:
  node_name: values.hostname
  keys:
    hostname: name
    osArch: values.architecture
    osFamily: values.osfamily
    osVersion: values.os.release.full
    osName: values.os.distro.description
    customfact: values.customfact
    virtual: values.virtual
    username: values.identity.user
```

and the script reads from puppet node directory (`/opt/puppetlabs/server/data/puppetserver/yaml/facts` by default) the file `mynode.yaml` which contains:
```yaml
name: mynode
parameters:
  hostname: mynode
  osfamily: Debian
  os:
    release:
      full: '9.4'
    lsb:
      distdescription: Debian GNU/Linux 9.4 (stretch)
  architecture: amd64
  lsbdistcodename: stretch
  mycustomfact: customvalue
  username: root
[...]
```

the output block describing this node will read:
```yaml
mynode:
  customfact: myCustomValue
  hostname: mynode.local.domain
  osArch: amd64
  osFamily: Debian
  osName: Debian GNU/Linux 10 (buster)
  osVersion: '10.4'
  tags:
  - Debian
  - '10.4'
  - hyperv
  - myCustomValue
  virtual: hyperv
  username: root
```

Each of the fields of the output block can be queried by Rundeck Node Filter.
