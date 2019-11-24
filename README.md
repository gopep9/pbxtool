# pbxtool  

## 说明  
这个项目是在搞ios混淆的时候弄出来的产物，现在能操作pbx文件的库有mod-pbxproj。然而这个库的可操作性感觉是比较弱的，例如我没有在这个库里面找到能添加节点的接口，或者是删除节点的接口，而这些功能在工程混淆的时候都是非常重要的，因此我自己实现了一个能更好地操作pbxproj文件的脚本  

## 使用方法  
### 初始化  
使用PbxTool类来加载xcode工程，例如  
`tool = PbxTool('project.pbxproj')`  
之后脚本会分析xcode工程，并且在构建树结构。  
### 保存  
使用  
`tool.save()`  
能够保存pbxproj为json格式（xcode10或以下版本的xcode不支持json格式的pbxproj，请使用save_xml1保存）  
### 获取里面的节点  
有多种方式可以获取其中的节点，例如  
`node = tool.get_node_by_uuid(uuid)`  
这个是可以根据uuid获取对应的节点  
之后可以访问和修改节点里面的参数，例如  
`node['name'] = 'main'`  

## 接口列表  
set_ios_sdk_path 设置ios sdk所在路径，在获取文件引用的路径时，假如存在系统framework，那么会使用这个路径来拼接framework的路径  
delete_null_node 这个函数是为了应付unity导出的工程的，因为unity导出工程总会有一个null节点，可以用这个方法删除这个空节点  
delete_node 删除某个节点，引用了这个节点的字符串也会被删除。例如被删除节点的uuid为7EFF499623573C8300C4535F，那么会遍历树中所有的字典和list，假如发现值为7EFF499623573C8300C4535F的话会把这个元素从字典或者是list中删除  
add_node 添加节点，返回该节点的随机生成的uuid  
add_node_with_uuid 指定uuid添加节点  
get_node_list_by_isa 获取某一类型的节点列表，例如PBXNativeTarget，具体类型由isa参数指定  
get_node_list_by_name 或者某一个名字的节点列表  
get_node_list_by_isa_and_name 指定类型和名字获取节点列表  
get_node_by_uuid 指定uuid获取节点  
get_uuid_by_node 获取节点本身的uuid  
get_project_node 获取project节点  
get_target_node 获取target节点，参数是这个target的名字  
get_build_configuration_node 根据target节点和和编译选项的名字（例如Debug）获取具体的编译选项节点  
get_build_configuration_name_list 获取target节点的编译选项节点列表  
get_build_phase_node 获取target的buildphase，isa指定类型，例如源码节点是PBXResourcesBuildPhase  
get_file_reference_node_from_build_file_node 在PBXBuildFile节点中获取PBXFileReference节点  
get_file_reference_node_list_from_build_file_node_list 根据PBXBuildFile节点列表获取PBXFileReference节点列表  
get_build_file_node_list_from_target 获取target的某个buildphase的buildfile节点列表  
get_main_group_node 获取mainGroup节点  
get_group_child_node 根据名字在父节点里获取子节点（PBXGroup专用）  
get_group_child_node_list 获取子节点列表  
get_father_node 获取子节点的父节点  
get_file_reference_node_path 获取PBXFileReference节点引用文件的绝对路径  
get_uuid_set_data 获取某节点依赖的uuid列表（不遍历获取到的uuid）  
get_uuid_list_depend_by_one_uuid 获取某节点依赖的节点列表（会遍历获取到的uuid，一直到全部依赖的uuid都包含进来）  
get_node_list_depend_by_one_node 上面函数的node版本  
clean_unuse_node 删除没人依赖的节点  
get_uuid_list 获取整个工程的uuid列表  
get_pbxpath 获取pbxproj文件的路径  
get_data 获取整个工程的数据（包含archiveVersion objectVersion objects等）  
get_objects 获取data中的objects  
save 保存为json格式  
save_xml1 保存为xml格式  

# pbxfunction  

## 说明  
这个文件是为了扩展pbxtool的功能而存在的  

## 函数说明  
add_target 添加target节点，target名字和里面的数据可以自定义，默认是使用脚本中的数据  
write_app_plist 添加app的info.plist到某个路径  
write_framework_plist 添加动态framework的info.plist到某个路径  
add_source_file_to_target 添加源码到某个target  
add_depend_target_framework 让某个target依赖另一个framework target  
add_copy_files_build_phase 某个target添加PBXCopyFilesBuildPhase节点  
add_frameworks_build_phase 某个target添加PBXFrameworksBuildPhase节点  
copy_build_configuration 某个target复制当前存在的某个buildConfiguration到新的buildConfiguration  
get_build_phase_path_list_from_target 能获取target的源文件列表或者是framework列表  
get_source_path_list_from_target 获取target源文件列表  
get_header_path_list_from_target 获取target头文件列表  
get_resource_path_list_from_target 获取target资源列表  
get_framework_path_list_from_target 获取target framework列表  
get_public_header_path_list_from_target framework保留的头文件列表  
get_source_path_list_from_target_and_dependency 获取target及其依赖的源文件列表  
get_header_path_list_from_target_and_dependency获取target及其依赖的头文件列表  
get_resource_path_list_from_target_and_dependency 获取target及其依赖的资源列表  
get_framework_path_list_from_target_and_dependency 获取target及其依赖的framework列表  
get_public_header_path_list_from_target_and_dependency 获取target及其依赖的public头文件列表  
get_product_name_list_from_target_and_dependency 获取target及其依赖的产品名列表  
get_pbx_path_list_from_target_and_dependency 获取target和所有依赖的工程的pbxproj文件路径  
change_file_reference_name 给某个filereference节点改名  
get_tool_list_from_target 获取target和所有依赖的工程的PbxTool实例列表  