#!/usr/local/bin/python3
#coding=utf-8

from pbxtool import PbxTool
import json
import os,sys
import copy
import pbxtool


#在这里封装各种实用的功能，例如添加一个target
#第三个参数可以自定义添加的json字符串，后续可以设计成不写死uuid
def add_target(tool,target_name,target_json_str=None):
    json_str = '''
{"7EFF499623573C8300C4535F": {"isa": "XCBuildConfiguration", "buildSettings": {"LD_RUNPATH_SEARCH_PATHS": ["$(inherited)", "@executable_path/Frameworks"], "INFOPLIST_FILE": "main/Info.plist", "CODE_SIGN_STYLE": "Automatic", "PRODUCT_BUNDLE_IDENTIFIER": "", "ASSETCATALOG_COMPILER_APPICON_NAME": "AppIcon", "TARGETED_DEVICE_FAMILY": "1,2", "PRODUCT_NAME": "$(TARGET_NAME)"}, "name": "Debug"}, "7EFF497B23573C8000C4535F": {"isa": "PBXSourcesBuildPhase", "buildActionMask": "2147483647", "files": [], "runOnlyForDeploymentPostprocessing": "0"}, "7EFF499723573C8300C4535F": {"isa": "XCBuildConfiguration", "buildSettings": {"LD_RUNPATH_SEARCH_PATHS": ["$(inherited)", "@executable_path/Frameworks"], "INFOPLIST_FILE": "main/Info.plist", "CODE_SIGN_STYLE": "Automatic", "PRODUCT_BUNDLE_IDENTIFIER": "", "ASSETCATALOG_COMPILER_APPICON_NAME": "AppIcon", "TARGETED_DEVICE_FAMILY": "1,2", "PRODUCT_NAME": "$(TARGET_NAME)"}, "name": "Release"}, "7EFF497D23573C8000C4535F": {"isa": "PBXResourcesBuildPhase", "buildActionMask": "2147483647", "files": [], "runOnlyForDeploymentPostprocessing": "0"}, "7EFF497E23573C8000C4535F": {"buildConfigurationList": "7EFF499523573C8300C4535F", "productReference": "7EFF497F23573C8000C4535F", "productType": "com.apple.product-type.application", "productName": "main", "isa": "PBXNativeTarget", "buildPhases": ["7EFF497B23573C8000C4535F", "7EFF497C23573C8000C4535F", "7EFF497D23573C8000C4535F"], "dependencies": [], "name": "main", "buildRules": []}, "7EFF497F23573C8000C4535F": {"path": "main.app", "isa": "PBXFileReference", "includeInIndex": "0", "explicitFileType": "wrapper.application", "sourceTree": "BUILT_PRODUCTS_DIR"}, "7EFF499523573C8300C4535F": {"isa": "XCConfigurationList", "defaultConfigurationIsVisible": "0", "defaultConfigurationName": "Release", "buildConfigurations": ["7EFF499623573C8300C4535F", "7EFF499723573C8300C4535F"]}, "7EFF497C23573C8000C4535F": {"isa": "PBXFrameworksBuildPhase", "buildActionMask": "2147483647", "files": [], "runOnlyForDeploymentPostprocessing": "0"}}
'''
    if target_json_str != None:
        json_str = target_json_str

    #这里跑随机替换uuid的逻辑
    data = json.loads(json_str)
    old_uuid_list = []
    for uuid in data:
        old_uuid_list.append(uuid)
    uuid_dict = {}
    new_uuid_list = []
    tool_uuid_list = tool.get_uuid_list()
    for old_uuid in old_uuid_list:
        new_uuid = pbxtool.generate_random_uuid(24)
        #假如重复了要再次生成
        while new_uuid in old_uuid_list or new_uuid in new_uuid_list or new_uuid in tool_uuid_list:
            print('遇到重复的uuid:')
            print(new_uuid)
            new_uuid = pbxtool.generate_random_uuid(24)
        new_uuid_list.append(new_uuid)
        uuid_dict[old_uuid] = new_uuid
    for old_uuid in uuid_dict:
        new_uuid = uuid_dict[old_uuid]
        json_str = json_str.replace(old_uuid,new_uuid)
    
    #这里加载这个json
    target_data = json.loads(json_str)
    target_node = None
    target_node_uuid = None
    for key in target_data:
        if target_data[key]['isa'] == 'PBXNativeTarget':
            target_node = target_data[key]
            target_node_uuid = key
    if target_node == None:
        raise Exception("pbxfunction add_target error. can not find PBXNativeTarget in data")
    #修改这个target里面的各种东西为指定的target名称
    target_node['productName'] = target_name
    target_node['name'] = target_name
    target_data[target_node['productReference']]['path'] = target_name + '.app'

    #配置每个BuildConfiguration
    for build_configuration_uuid in target_data[target_node['buildConfigurationList']]['buildConfigurations']:
        target_data[build_configuration_uuid]['buildSettings']['INFOPLIST_FILE'] = target_name + '/Info.plist'

    #遍历添加节点到tool
    for key in target_data:
        tool.add_node_with_uuid(target_data[key],key)

    #配置原工程添加这个target，在工程节点的TargetAttributes和targets都要添加
    project_node = tool.get_project_node()
    project_node['targets'].append(target_node_uuid)
    project_node['attributes']['TargetAttributes'][target_node_uuid] = {'CreatedOnToolsVersion':'11.1'}

    #注意后续还要加info.plist

def write_app_plist(path):
    plist_str = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleDevelopmentRegion</key>
	<string>$(DEVELOPMENT_LANGUAGE)</string>
	<key>CFBundleExecutable</key>
	<string>$(EXECUTABLE_NAME)</string>
	<key>CFBundleIdentifier</key>
	<string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
	<key>CFBundleInfoDictionaryVersion</key>
	<string>6.0</string>
	<key>CFBundleName</key>
	<string>$(PRODUCT_NAME)</string>
	<key>CFBundlePackageType</key>
	<string>$(PRODUCT_BUNDLE_PACKAGE_TYPE)</string>
	<key>CFBundleShortVersionString</key>
	<string>1.0</string>
	<key>CFBundleVersion</key>
	<string>1</string>
	<key>LSRequiresIPhoneOS</key>
	<true/>
	<key>UIApplicationSceneManifest</key>
	<dict>
		<key>UIApplicationSupportsMultipleScenes</key>
		<false/>
		<key>UISceneConfigurations</key>
		<dict>
			<key>UIWindowSceneSessionRoleApplication</key>
			<array>
				<dict>
					<key>UISceneConfigurationName</key>
					<string>Default Configuration</string>
					<key>UISceneDelegateClassName</key>
					<string>SceneDelegate</string>
					<key>UISceneStoryboardFile</key>
					<string>Main</string>
				</dict>
			</array>
		</dict>
	</dict>
	<key>UILaunchStoryboardName</key>
	<string>LaunchScreen</string>
	<key>UIMainStoryboardFile</key>
	<string>Main</string>
	<key>UIRequiredDeviceCapabilities</key>
	<array>
		<string>armv7</string>
	</array>
	<key>UISupportedInterfaceOrientations</key>
	<array>
		<string>UIInterfaceOrientationPortrait</string>
		<string>UIInterfaceOrientationLandscapeLeft</string>
		<string>UIInterfaceOrientationLandscapeRight</string>
	</array>
	<key>UISupportedInterfaceOrientations~ipad</key>
	<array>
		<string>UIInterfaceOrientationPortrait</string>
		<string>UIInterfaceOrientationPortraitUpsideDown</string>
		<string>UIInterfaceOrientationLandscapeLeft</string>
		<string>UIInterfaceOrientationLandscapeRight</string>
	</array>
</dict>
</plist>
'''
    local_dir = os.path.split(path)[0]
    if not os.path.isdir(local_dir):
        os.makedirs(local_dir)
    with open(path,'w') as f:
        f.write(plist_str)

def write_framework_plist(path):
    plist_str = '''
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleDevelopmentRegion</key>
	<string>$(DEVELOPMENT_LANGUAGE)</string>
	<key>CFBundleExecutable</key>
	<string>$(EXECUTABLE_NAME)</string>
	<key>CFBundleIdentifier</key>
	<string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
	<key>CFBundleInfoDictionaryVersion</key>
	<string>6.0</string>
	<key>CFBundleName</key>
	<string>$(PRODUCT_NAME)</string>
	<key>CFBundlePackageType</key>
	<string>FMWK</string>
	<key>CFBundleShortVersionString</key>
	<string>1.0</string>
	<key>CFBundleVersion</key>
	<string>1.0.0.0</string>
</dict>
</plist>
'''
    local_dir = os.path.split(path)[0]
    if not os.path.isdir(local_dir):
        os.makedirs(local_dir)
    with open(path,'w') as f:
        f.write(plist_str)


#添加cpp源码到某个target
#cpp sourcecode.cpp.cpp
#mm sourcecode.cpp.objcpp
#m sourcecode.c.objc
def add_source_file_to_target(tool,source_path,target_name,lastKnownFileType):
    source_name = os.path.split(source_path)[1]
    #添加文件引用节点
    source_file_reference_uuid = tool.add_node({
        'isa':'PBXFileReference',
        'lastKnownFileType':lastKnownFileType,
        'name':source_name,
        'path':source_path,
        'sourceTree':'<group>'
    })
    #添加buildfile节点，引用上面的节点
    build_file_uuid = tool.add_node({'isa':'PBXBuildFile','fileRef':source_file_reference_uuid})
    #在SourcesBuildPhase中添加buildfile节点
    target_node = tool.get_target_node(target_name)
    sources_build_phase_node = tool.get_build_phase_node(target_node,PbxTool.PBXSourcesBuildPhase)
    sources_build_phase_node['files'].append(build_file_uuid)
    #在maingroup中添加文件节点
    main_group = tool.get_main_group_node()
    main_group['children'].append(source_file_reference_uuid)



#让main_target依赖framework_framework
def add_depend_target_framework(tool,main_target_name,framework_target_name):
    #加PBXTargetDependency
    #加PBXContainerItemProxy
    #在PBXContainerItemProxy会引用被依赖的节点和根节点
    main_target_node = tool.get_target_node(main_target_name)
    framework_target_node = tool.get_target_node(framework_target_name)
    main_target_uuid = tool.get_uuid_by_node(main_target_node)
    framework_target_uuid = tool.get_uuid_by_node(framework_target_node)

    #添加PBXContainerItemProxy
    rootObject_uuid = tool.get_uuid_by_node(tool.get_project_node())

    container_item_proxy_uuid = tool.add_node({
        'isa':'PBXContainerItemProxy',
        'containerPortal':rootObject_uuid,
        'proxyType':'1',
        'remoteGlobalIDString':framework_target_uuid,
        'remoteInfo':framework_target_name
    })

    target_dependency_uuid = tool.add_node({'isa':'PBXTargetDependency','target':framework_target_uuid,'targetProxy':container_item_proxy_uuid})

    #在main target中添加depend节点
    main_target_node['dependencies'].append(target_dependency_uuid)

    #处理文件节点
    #先找到framework_target的产品文件节点（直接在target中找productReference）
    #之后要创建一个buildfile节点，依赖上面的节点，并且添加CodeSignOnCopy、RemoveHeadersOnCopy等属性
    #在main_target的PBXCopyFilesBuildPhase中添加上面的buildfile节点
    #创建buildfile节点，依赖产品节点，添加的frameworkbuildphase

    framework_product_reference_uuid = framework_target_node['productReference']

    #复制phase节点
    copy_build_file_uuid = tool.add_node({
        'isa':'PBXBuildFile',
        'fileRef':framework_product_reference_uuid,
        'settings':{
            'ATTRIBUTES':['CodeSignOnCopy','RemoveHeadersOnCopy']
        }
    })

    #创建copyphase
    add_copy_files_build_phase(tool,main_target_name)
    tool.get_build_phase_node(main_target_node,PbxTool.PBXCopyFilesBuildPhase)['files'].append(copy_build_file_uuid)

    #framework phase节点
    framework_build_file_uuid = tool.add_node({
        'isa':'PBXBuildFile',
        'fileRef':framework_product_reference_uuid
    })

    #创建frameworkphase
    add_frameworks_build_phase(tool,main_target_name)
    tool.get_build_phase_node(main_target_node,PbxTool.PBXFrameworksBuildPhase)['files'].append(framework_build_file_uuid)

#为某个target创建PBXCopyFilesBuildPhase节点
def add_copy_files_build_phase(tool,target_name):
    target_node = tool.get_target_node(target_name)
    if tool.get_build_phase_node(target_node,PbxTool.PBXCopyFilesBuildPhase) == None:
        copy_files_build_phase_uuid = tool.add_node({
            'isa':'PBXCopyFilesBuildPhase',
            'buildActionMask':'2147483647',
            'dstPath':'',
            'dstSubfolderSpec':'10',
            'files':[],
            'name':'Embed Frameworks',
            'runOnlyForDeploymentPostprocessing':'0'
        })
        target_node['buildPhases'].append(copy_files_build_phase_uuid)
    return tool.get_build_phase_node(target_node,PbxTool.PBXCopyFilesBuildPhase)

#创建PBXFrameworksBuildPhase节点
def add_frameworks_build_phase(tool,target_name):
    target_node = tool.get_target_node(target_name)
    if tool.get_build_phase_node(target_node,PbxTool.PBXFrameworksBuildPhase) == None:
        #确认不存在才创建
        frameworks_build_phase_uuid = tool.add_node({
            'isa':'PBXFrameworksBuildPhase',
            'buildActionMask':'2147483647',
            'files':[],
            'runOnlyForDeploymentPostprocessing':'0'
        })
        target_node['buildPhases'].append(frameworks_build_phase_uuid)
    return tool.get_build_phase_node(target_node,PbxTool.PBXFrameworksBuildPhase)


#创建PBXResourcesBuildPhase节点
def add_resources_build_phase(tool,target_name):
    target_node = tool.get_target_node(target_name)
    if tool.get_build_phase_node(target_node,PbxTool.PBXResourcesBuildPhase) == None:
        resources_build_phase_uuid = tool.add_node({
            'isa':'PBXResourcesBuildPhase',
            'buildActionMask':'2147483647',
            'files':[],
            'runOnlyForDeploymentPostprocessing':'0'
        })
        target_node['buildPhases'].append(resources_build_phase_uuid)
    return tool.get_build_phase_node(target_node,PbxTool.PBXResourcesBuildPhase)

#创建指定名称的XCBuildConfiguration节点
def copy_build_configuration(tool,target_name,new_build_configuration_name,source_build_configuration_name):
    target_node = tool.get_target_node(target_name)
    if tool.get_build_configuration_node(target_node,new_build_configuration_name) == None:
        #不存在这个build configuration的时候才复制
        source_build_configuration_node = tool.get_build_configuration_node(target_node,source_build_configuration_name)
        build_configuration_uuid = tool.add_node({
            'isa':'XCBuildConfiguration',
            'name':new_build_configuration_name,
            'buildSettings':copy.deepcopy(source_build_configuration_node['buildSettings'])
        })
        #在buildconfigurationlist中添加新建的节点
        build_configuration_list = tool.get_node_by_uuid(target_node['buildConfigurationList'])
        build_configuration_list['buildConfigurations'].append(build_configuration_uuid)
        return build_configuration_uuid
    return None


#获取target中的某样东西的文件节点路径列表（源码、framework、头文件、资源），里面可能会有none，代表这个东西是子工程或者target生成出来的
def get_build_phase_path_list_from_target(tool,target_name,isa):
    target_node = tool.get_target_node(target_name)
    build_file_node_list = tool.get_build_file_node_list_from_target(target_node,isa)
    file_reference_node_list = tool.get_file_reference_node_list_from_build_file_node_list(build_file_node_list)
    path_list = []
    for file_reference_node in file_reference_node_list:
        path_list.append(tool.get_file_reference_node_path(file_reference_node))
    return path_list

#列出这个target依赖的源码文件节点路径列表
def get_source_path_list_from_target(tool,target_name):
    return get_build_phase_path_list_from_target(tool,target_name,PbxTool.PBXSourcesBuildPhase)

#列出头文件节点路径列表
def get_header_path_list_from_target(tool,target_name):
    return get_build_phase_path_list_from_target(tool,target_name,PbxTool.PBXHeadersBuildPhase)

#列出资源节点路径列表
def get_resource_path_list_from_target(tool,target_name):
    return get_build_phase_path_list_from_target(tool,target_name,PbxTool.PBXResourcesBuildPhase)

#列出framework节点路径列表
def get_framework_path_list_from_target(tool,target_name):
    return get_build_phase_path_list_from_target(tool,target_name,PbxTool.PBXFrameworksBuildPhase)

#列出framework的暴露出来的头文件
def get_public_header_path_list_from_target(tool,target_name):
    target_node = tool.get_target_node(target_name)
    build_file_node_list = tool.get_build_file_node_list_from_target(target_node,PbxTool.PBXHeadersBuildPhase)
    public_header_path_list = []
    for build_file_node in build_file_node_list:
        if 'settings' in build_file_node and 'ATTRIBUTES' in build_file_node['settings'] and 'Public' in build_file_node['settings']['ATTRIBUTES']:
            file_reference_node = tool.get_file_reference_node_from_build_file_node(build_file_node)
            public_header_path_list.append(tool.get_file_reference_node_path(file_reference_node))
    return public_header_path_list


#这里直接获取某个target的product
def get_product_name_list_from_target(tool,target_name):
    target_node = tool.get_target_node(target_name)
    product_name = tool.get_node_by_uuid(target_node['productReference'])['path']
    return [product_name]

#获取pbx文件所在列表，这里返回的是一个列表（兼容下面的逻辑）
def get_pbx_path_list_from_target(tool,target_name):
    # target_node = tool.get_target_node(target_name)
    return [tool.get_pbxpath()]


#遍历target和子target获取某种节点，第三个是个回调函数，决定要添加每个target中的什么东西进去
#这个函数其实可以更多自定义，获取子target的某些东西
def get_something_list_from_target_and_dependency(tool,target_name,get_some_thing_list_func,some_thing_list = None):
    if some_thing_list is None:
        some_thing_list = []
    target_node = tool.get_target_node(target_name)
    #先遍历子target
    for target_dependency_uuid in target_node['dependencies']:
        target_dependency_node = tool.get_node_by_uuid(target_dependency_uuid)
        container_item_proxy_node = tool.get_node_by_uuid(target_dependency_node['targetProxy'])
        container_portal_node = tool.get_node_by_uuid(container_item_proxy_node['containerPortal'])
        if container_portal_node['isa'] == PbxTool.PBXProject:
            #依赖的target还在本工程
            child_target_node = tool.get_node_by_uuid(container_item_proxy_node['remoteGlobalIDString'])
            child_target_name = child_target_node['name']
            get_something_list_from_target_and_dependency(tool,child_target_name,get_some_thing_list_func,some_thing_list)
        elif container_portal_node['isa'] == PbxTool.PBXFileReference:
            #依赖的target在其它工程
            child_project_pbx_path = os.path.join(tool.get_file_reference_node_path(container_portal_node),'project.pbxproj')
            child_tool = PbxTool(child_project_pbx_path)
            child_target_node = child_tool.get_node_by_uuid(container_item_proxy_node['remoteGlobalIDString'])
            child_target_name = child_target_node['name']
            get_something_list_from_target_and_dependency(child_tool,child_target_name,get_some_thing_list_func,some_thing_list)
    #添加当前工程的list
    some_thing_list += get_some_thing_list_func(tool,target_name)
    return some_thing_list


#列出某个target依赖的文件节点以及这个target依赖的子target的文件节点
#这四个函数和上面四个函数差不多，只不过连依赖的target都获取路径
def get_source_path_list_from_target_and_dependency(tool,target_name):
    return list(set(get_something_list_from_target_and_dependency(tool,target_name,get_source_path_list_from_target)))

def get_header_path_list_from_target_and_dependency(tool,target_name):
    return list(set(get_something_list_from_target_and_dependency(tool,target_name,get_header_path_list_from_target)))

def get_resource_path_list_from_target_and_dependency(tool,target_name):
    return list(set(get_something_list_from_target_and_dependency(tool,target_name,get_resource_path_list_from_target)))

def get_framework_path_list_from_target_and_dependency(tool,target_name):
    return list(set(get_something_list_from_target_and_dependency(tool,target_name,get_framework_path_list_from_target)))

#获取某工程及其依赖的target的头文件路径列表
def get_public_header_path_list_from_target_and_dependency(tool,target_name):
    return list(set(get_something_list_from_target_and_dependency(tool,target_name,get_public_header_path_list_from_target)))

def get_product_name_list_from_target_and_dependency(tool,target_name):
    return list(set(get_something_list_from_target_and_dependency(tool,target_name,get_product_name_list_from_target)))

def get_pbx_path_list_from_target_and_dependency(tool,target_name):
    return list(set(get_something_list_from_target_and_dependency(tool,target_name,get_pbx_path_list_from_target)))

#修改某个filereference的文件名(name和path都改，name可能不存在)，并且修改实际的文件名
def change_file_reference_name(tool,file_reference_node,new_name):
    old_path = tool.get_file_reference_node_path(file_reference_node)
    #这里要考虑三种情况 原来节点有name 有path 有name和path
    if 'name' in file_reference_node:
        file_reference_node['name'] = new_name
    if 'path' in file_reference_node:
        file_reference_node['path'] = os.path.join(os.path.split(file_reference_node['path'])[0],new_name)
        new_path = os.path.join(os.path.split(old_path)[0],new_name)
        #只有在存在真实的path的时候才做重命名逻辑，假如只有name而没有path的话这个节点不对应真实的目录
        os.rename(old_path,new_path)

#获取某项目依赖的其它项目的工程节点，为多工程混淆作准备
def get_tool_list_from_target(tool,target_name):
    target_node = tool.get_target_node(target_name)
    tool_list = []
    for target_dependency_uuid in target_node['dependencies']:
        target_dependency_node = tool.get_node_by_uuid(target_dependency_uuid)
        container_item_proxy_node = tool.get_node_by_uuid(target_dependency_node['targetProxy'])
        container_portal_node = tool.get_node_by_uuid(container_item_proxy_node['containerPortal'])
        if container_portal_node['isa'] == PbxTool.PBXFileReference:
            child_project_pbx_path = os.path.join(tool.get_file_reference_node_path(container_portal_node),'project.pbxproj')
            child_tool = PbxTool(child_project_pbx_path)
            tool_list.append(child_tool)
    return tool_list
