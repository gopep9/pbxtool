#!/usr/local/bin/python3
#coding=utf-8

import os,sys
import re
from subprocess import getstatusoutput
import json
import copy
import random

#使用这个键在每个节点存放自己的uuid
pbxtool_uuid = 'pbxtool_uuid'

#用于生成自定义的节点的uuid
def generate_random_uuid(randomlength=24):
    """
    生成一个指定长度的随机字符串
    """
    random_str = ''
    base_str = 'ABCDEF0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str

class PbxTool(object):
    #初始化，使用pbxproj读取工程文件

    # 定义各种变量，方便查找各种节点的名字
    # 项目，target相关
    PBXProject = 'PBXProject'
    PBXNativeTarget = 'PBXNativeTarget'

    #引用相关
    PBXBuildFile = 'PBXBuildFile'
    PBXFileReference = 'PBXFileReference'
    PBXGroup = 'PBXGroup'
    PBXTargetDependency = 'PBXTargetDependency'
    PBXContainerItemProxy = 'PBXContainerItemProxy'
    PBXReferenceProxy = 'PBXReferenceProxy'
    PBXVariantGroup = 'PBXVariantGroup'

    #各种BuildPhase
    PBXCopyFilesBuildPhase = 'PBXCopyFilesBuildPhase'
    PBXFrameworksBuildPhase = 'PBXFrameworksBuildPhase'
    PBXHeadersBuildPhase = 'PBXHeadersBuildPhase'
    PBXResourcesBuildPhase = 'PBXResourcesBuildPhase'
    PBXShellScriptBuildPhase = 'PBXShellScriptBuildPhase'
    PBXSourcesBuildPhase = 'PBXSourcesBuildPhase'

    #编译配置
    XCBuildConfiguration = 'XCBuildConfiguration'
    XCConfigurationList = 'XCConfigurationList'

    def __init__(self,pbxpath):
        super(PbxTool, self).__init__()
        if pbxpath.endswith('.xcodeproj'):
            pbxpath = os.path.join(pbxpath,'project.pbxproj')
        status, output = getstatusoutput('plutil -convert json -o - {}'.format(pbxpath))
        if status:
            raise Exception('plutil error: {}'.format(output))

        self.pbxpath = os.path.abspath(pbxpath)
        self.data = json.loads(output)
        self.objects = self.data['objects']

        #在每个对象中添加标式起uuid
        for key in self.objects:
            self.objects[key][pbxtool_uuid] = key
        
        #苹果sdk所在路径
        self.ios_sdk_path = '/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk'
    
    def set_ios_sdk_path(self,ios_sdk_path):
        self.ios_sdk_path = ios_sdk_path
        
    #找到某个类型的空节点，并且把它删掉
    def delete_null_node(self,isa):
        tmp_dict = copy.deepcopy(self.objects)
        for key in tmp_dict:
            if key in self.objects:
                if self.objects[key]['isa'] == isa:
                    if(len(self.objects[key]) == 1):
                        #只有这一个元素
                        self.delete_node(self.objects[key])
    
    #删除某个节点和其它节点对这个节点的依赖
    def delete_node(self,node):
        if node == None:
            return
        uuid = self.get_uuid_by_node(node)
        del self.objects[self.get_uuid_by_node(node)]
        #递归删除引用这个uuid的节点
        def delete_node_in_other_node(node,uuid,delete_node_list):
            if isinstance(node,dict):
                for key in node:
                    delresult = delete_node_in_other_node(node[key],uuid,delete_node_list)
                    if delresult == None:
                        delete_node_list.append((node,key))
            elif isinstance(node,list):
                for i in range(len(node)):
                    delresult = delete_node_in_other_node(node[i],uuid,delete_node_list)
                    if delresult == None:
                        delete_node_list.append((node,i))
            elif isinstance(node,str):
                if node == uuid:
                    return None
            return node
        delete_node_list = []
        delete_node_in_other_node(self.objects,uuid,delete_node_list)
        for i in delete_node_list:
            node = i[0]
            key = i[1]
            del node[key]

    #添加节点，返回生成节点的uuid
    def add_node(self,nodeContent):
        uuid = generate_random_uuid(24)
        while True: #一直生成直到和现有的uuid不重复
            if uuid not in self.objects:
                break
            uuid = generate_random_uuid(24)
        tmp = copy.deepcopy(nodeContent)
        tmp[pbxtool_uuid] = uuid
        self.objects[uuid] = tmp
        return uuid

    def add_node_with_uuid(self,nodeContent,uuid):
        tmp = copy.deepcopy(nodeContent)
        tmp[pbxtool_uuid] = uuid
        self.objects[uuid] = tmp
        return uuid

    #获取各种类型节点列表
    def get_node_list_by_isa(self,isa):
        node_list = []
        for key in self.objects:
            if self.objects[key]['isa'] == isa:
                node_list.append(self.objects[key])
        return node_list

    #根据名字获取节点列表
    def get_node_list_by_name(self,name):
        node_list = []
        for key in self.objects:
            if 'name' in self.objects[key] and self.objects[key]['name'] == name:
                node_list.append(self.objects[key])

    #根据名字和isa获取节点列表
    def get_node_list_by_isa_and_name(self,isa,name):
        isa_node_list = self.get_node_list_by_isa(isa)
        result_list = []
        for node in isa_node_list:
            if 'name' in node and node['name'] == name:
                result_list.append(node)
        return result_list

    #获取指定的uuid节点
    def get_node_by_uuid(self,uuid):
        if uuid in self.objects:
            return self.objects[uuid]
        return None

    #获取某个节点的uuid，假如没有找到的话返回None值，是否会返回存在两个相同的节点。。。
    def get_uuid_by_node(self,node):
        return node[pbxtool_uuid]

    #获取project节点
    def get_project_node(self):
        return self.get_node_list_by_isa(PbxTool.PBXProject)[0]

    #获取target节点
    def get_target_node(self,target_name):
        target_list = self.get_node_list_by_isa(PbxTool.PBXNativeTarget)
        for target_node in target_list:
            if target_node['name'] == target_name:
                return target_node
        return None
        
    #获取编译配置，参数是target节点，编译选项的名字（Debug之类的）
    def get_build_configuration_node(self,target_node,build_configuration_name):
        build_configuration_list = self.get_node_by_uuid(target_node['buildConfigurationList'])
        for build_configuration in build_configuration_list['buildConfigurations']:
            build_configuration_node = self.get_node_by_uuid(build_configuration)
            if build_configuration_node['name'] == build_configuration_name:
                return build_configuration_node
        return None

    #获取某个target有多少种编译配置
    def get_build_configuration_name_list(self,target_node):
        name_list = []
        build_configuration_list = self.get_node_by_uuid(target_node['buildConfigurationList'])
        for build_configuration in build_configuration_list['buildConfigurations']:
            build_configuration_node = self.get_node_by_uuid(build_configuration)
            name_list.append(build_configuration_node['name'])
        return name_list

    #获取buildPhases节点，参数是target的节点和isa的值
    def get_build_phase_node(self,target_node,isa):
        build_phase_list = target_node['buildPhases']
        for build_phase in build_phase_list:
            build_phase_node = self.get_node_by_uuid(build_phase)
            if build_phase_node['isa'] == isa:
                return build_phase_node
        return None

    #在buildFile节点中获取获取fileReference节点
    def get_file_reference_node_from_build_file_node(self,build_file_node):
        file_reference = build_file_node['fileRef']
        return self.get_node_by_uuid(file_reference)

    def get_file_reference_node_list_from_build_file_node_list(self,build_file_node_list):
        file_reference_node_list = []
        for build_file_node in build_file_node_list:
            file_reference_node_list.append(self.get_file_reference_node_from_build_file_node(build_file_node))
        return file_reference_node_list

    #获取某个target的编译文件节点列表，在获取的基础上可以获取文件路径，编译选项之类的东西（文件路径可能要专门写个函数来弄）
    def get_build_file_node_list_from_target(self,target_node,isa):
        some_build_phase = self.get_build_phase_node(target_node,isa)
        if some_build_phase == None:
            return []
        build_file_node_list = []
        for build_file in some_build_phase['files']:
            build_file_node = self.get_node_by_uuid(build_file)
            build_file_node_list.append(build_file_node)
        return build_file_node_list


    #获取maingroup节点，可能还需要获取其它group或者是文件的节点
    def get_main_group_node(self):
        return self.get_node_by_uuid(self.get_project_node()['mainGroup'])

    #获取某个group节点下的group节点或者FileReference节点
    def get_group_child_node(self,father_node,node_name):
        for children_uuid in father_node['children']:
            children_node = self.get_node_by_uuid(children_uuid)
            if 'name' in children_node and children_node['name'] == node_name or 'path' in children_node and os.path.split(children_node['path'])[1] == node_name:
                return children_node
        return None

    #获取子节点列表
    def get_group_child_node_list(self,father_node):
        children_node_list = []
        for children_uuid in father_node['children']:
            children_node = self.get_node_by_uuid(children_uuid)
            children_node_list.append(children_node)
        return children_node_list

    #查找某个节点在哪个PBXGroup中
    def get_father_node(self,node):
        uuid = self.get_uuid_by_node(node)
        for group_node in self.get_node_list_by_isa(PbxTool.PBXGroup):
            for child_uuid in group_node['children']:
                if child_uuid == uuid:
                    return group_node
        return None

    #写一个函数在不停查找自己的母group直到maingroup，只接受sourceTree为<group>的节点
    def _build_group_or_file_reference_path(self,node):
        #maingroup没有path
        current_node_path = ''
        if 'path' not in node:
            current_node_path = '.'
        else:
            current_node_path = node['path']
        father_node = self.get_father_node(node)
        father_node_path = ''
        if father_node == None:
            #假如node是maingroup的话就会跑到这里
            father_node_path = ''
        elif father_node['sourceTree'] != '<group>': 
            raise Exception("error, the father node in _build_group_or_file_reference_path sourceTree value is %s and not <group>"%father_node['sourceTree'])
        else:
            father_node_path = self._build_group_or_file_reference_path(father_node)
        return os.path.join(father_node_path,current_node_path)
        
    #获取某个fileReference节点的路径（绝对路径），其实也可以获取group的路径
    def get_file_reference_node_path(self,file_reference_node):
        file_reference_node_path = '.'
        if 'path' in file_reference_node:
            file_reference_node_path = file_reference_node['path']
        file_reference_node_uuid = self.get_uuid_by_node(file_reference_node)

        #获取工程所在目录
        xcodeproj_path = os.path.split(os.path.realpath(self.pbxpath))[0]
        source_root = os.path.join(xcodeproj_path,'..')

        if file_reference_node['sourceTree'] == '<group>':
            #是group中的fileReference节点
            #后一部分的文件路径，以xcode工程所在的根目录为起点
            last_path = self._build_group_or_file_reference_path(file_reference_node)
            return os.path.join(source_root,last_path)

        elif file_reference_node['sourceTree'] == 'SOURCE_ROOT':
            #是源工程(xcodeproj所在的路径)
            # last_path = file_reference_node_path
            return os.path.join(source_root,file_reference_node_path)

        elif file_reference_node['sourceTree'] == 'SDKROOT':
            #苹果库所在路径
            return os.path.join(self.ios_sdk_path,file_reference_node_path)
            
        elif file_reference_node['sourceTree'] == 'BUILT_PRODUCTS_DIR':
            # 生成目录，这个tm要怎么处理，还是直接返回一个bool代表是否是生成目录。。。
            
            #直接返回None算了，反正也不多用
            return None
        return None

    #列出在某个数据节点依赖的uuid列表
    def get_uuid_set_data(self,data):
        uuid_set = set()
        if isinstance(data,dict):
            for key in data:
                uuid_set = uuid_set | self.get_uuid_set_data(data[key])
        elif isinstance(data,list):
            for child_data in data:
                uuid_set = uuid_set | self.get_uuid_set_data(child_data)
        elif isinstance(data,str):
            if re.match('([0-9A-F]{24})',data):
                uuid_set.add(data)
        return uuid_set

    #获取某个uuid节点依赖的所有其它uuid，为复制做准备，重复遍历问题
    def get_uuid_list_depend_by_one_uuid(self,uuid):
        result_set = set() #这个是最终要返回的set（list）
        result_set.add(uuid)
        have_through_set = set() #记录哪些uuid已经被遍历，防止无限循环
        current_uuid = uuid #当前遍历的uuid
        while True:                
            result_set = result_set | self.get_uuid_set_data(self.get_node_by_uuid(current_uuid))
            have_through_set.add(current_uuid)
            if result_set == have_through_set: #遍历完成
                break
            current_uuid = list(result_set - have_through_set)[0]
        return list(result_set)

    #上面的函数的node版本，某些在当前工程不存在的节点不会加入返回值
    def get_node_list_depend_by_one_node(self,node):
        uuid_list = self.get_uuid_list_depend_by_one_uuid(self.get_uuid_by_node(node))
        node_list = []
        for uuid in uuid_list:
            node_list.append(self.get_node_by_uuid(uuid))
        return node_list


    #删除没有人依赖的节点
    def clean_unuse_node(self):
        inuse_uuid_list = self.get_uuid_list_depend_by_one_uuid(self.data['rootObject'])
        unuse_uuid_set = set(self.objects) - set(inuse_uuid_list)
        for uuid in unuse_uuid_set:
            del self.objects[uuid]

    def get_uuid_list(self):
        uuid_list = []
        for uuid in self.objects:
            uuid_list.append(uuid)
        return uuid_list

    def get_pbxpath(self):
        return self.pbxpath

    def get_data(self):
        return self.data

    def get_objects(self):
        return self.objects

    #保存
    def save(self,path=None):
        if path == None:
            path = self.pbxpath
        #这里不能把pbxtool_uuid也导出去
        tmp = copy.deepcopy(self.data)
        for key in tmp['objects']:
            del tmp['objects'][key][pbxtool_uuid]
        try:
            with open(path, 'w') as f:
                json.dump(tmp,f,sort_keys=True, indent=4)
        except Exception as e:
            print("{} write json error".format(path))

    #保存为xml1格式，xcode10及以下版本的xcode也能识别
    def save_xml1(self,path=None):
        self.save()
        if path == None:
            path = self.pbxpath
        status, output = getstatusoutput('plutil -convert xml1 "%s"'%path)
        if status:
            raise Exception('plutil error: {}'.format(output))
    

if __name__ == '__main__':
    tool = PbxTool(sys.argv[1])
