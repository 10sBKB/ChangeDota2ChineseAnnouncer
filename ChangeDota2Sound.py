import os
import tkinter
from tkinter import filedialog
from rich import print
import re
import zipfile
import shutil

class ChangeDota2Sound() :
    gamePath = ''
    checkDirIndex = ('dota','dota_schinese','dota/sounds/vo')
    modifyFileList = ('dota/pak01_dir.vpk','dota_schinese/pak01_dir.vpk')
    moveFilePath  = 'dota/sounds/vo'
    moveFile = 'announcer'
    notFindDirs = []
    helpYouCreateDirs = True
    modifyStr = 'sounds/vo/announcer\x00'
    changedStr = 'sounds/vo/announce0\x00'
    saveEncode = 'mbcs'
    replaceFileName = 'pak01_dir.vpk'
    replaceFileBackName = 'pak01_dir.vpk.back'

    # 获取游戏game路径
    def get_dota_url(self) :
        print('选择dota2文件夹下 game 文件夹')
        print('尝试获取记录路径数据')
        try :
            # 历史
            hisFile = open('path.txt','r',encoding='utf-8')
            path = hisFile.read()
            if not path :
                raise Exception('历史文件无内容!')
        except :
            # 选择
            print('无历史数据,开始选择路径')
            app = tkinter.Tk()
            app.title('修改Dota2中文播报')
            path = filedialog.askdirectory(title='选择STEAM -> steamapps -> common -> dota 2 beta -> game文件夹!')
        
            # 存储
            try :
                newFile = open('path.txt','w',encoding='utf-8')
            except Exception as e :
                print('创建记录文件失败!',e)
                return False
            else :
                try :
                    newFile.write(path)
                except Exception as e :
                    print('写入记录失败!',e)
                    return False
                else :
                    print('记录存储成功!')
        finally :
            self.gamePath = path
            print('成功获取Dota2路径')
            print('选择路径:'+path)
            return path

    # 检查游戏路径
    def check_path(self,path) :
        print('开始检查路径有效性')
        allFind = True
        for i in range(len(self.checkDirIndex)) :
            check = '%s/%s'%(path,self.checkDirIndex[i])
            try:
                if not os.path.exists(check) :
                    raise Exception('未发现路径: %s'%(check))
            except Exception as e :
                print(e)
                allFind = False
                self.notFindDirs.append(self.checkDirIndex[i])
            else :
                print('目录: %s 已被发现!'%(self.checkDirIndex[i]))
        if allFind is True :
            print('路径完整!')
            return True
        else :
            print('路径不完整!')
            return False

    # 执行修改流程
    def changeStart(self) :
        gamePath = self.get_dota_url()
        if gamePath is False :
            print('修改失败! 获取路径失败!')
            return False
        
        if not self.check_path(gamePath) :
            print('缺少如下路径:')
            for i in range(len(self.notFindDirs)) :
                print(self.gamePath+'/'+self.notFindDirs[i])
            print('请确认是否正确选择Dota2的game路径?')

            # 是否创建目录?
            if self.helpYouCreateDirs :
                print('如果你认为路径没错,是否创建缺少的路径?')
                isCreate = ''
                while True :
                    isCreate = str(input('yes/no :'))
                    if isCreate == 'yes' :
                        # 创建路径
                        if self.createDirs(self.notFindDirs) :
                            print('创建目录成功!')
                            self.changeStart()
                            quit()
                        else :
                            print('创建目录失败!')
                            return False    
                    elif isCreate == 'no' :
                        print('缺少路径! 修改失败!')
                        pathFile = open('path.txt','w',encoding='utf-8')
                        pathFile.close()
                        return False
            else :
                # 无提示结束
                print('缺少路径! 修改失败!')
                pathFile = open('path.txt','w',encoding='utf-8')
                pathFile.close()
                return False


        if  not self.remove_file() :
            print ('移动文件失败!')
            return False

        if self.modifyFile() and self.remove_file() :
            print('修改成功!')
            return True
        else :
            print('修改失败!')
            return False
    
    # 修改游戏配音文件
    def modifyFile(self) :
        # 文件检测
        for i in range(len(self.modifyFileList)) :
            path  = self.modifyFileList[i]
            pathToFile = self.gamePath+'/'+path
            if not os.path.exists(pathToFile) :
                print('缺少文件 修改失败!:')
                print(self.gamePath+'/'+path)
                return False
            # 开始修改
            else :
                originFile = open(pathToFile,'r+',encoding='utf-8',errors='ignore')
                content = originFile.read()
                allChanged = True
                # 正常修改
                if (content.count(self.modifyStr) == 1) and (content.replace(self.modifyStr,self.changedStr,1)) :
                    print(path+'发现修改节点!')
                    if not self.replaceFile(pathToFile) :
                        print('替换文件数据失败!')
                        allChanged = False
                    print(path+'文件修改成功!')
                # 是否为已修改
                elif (content.count(self.changedStr) == 1) :
                    # 已修改 是否重置
                    print(path+'文件已被修改,是否重置?') 
                    while True :
                        inputStr = input('yes/no : ')
                        if(inputStr == 'yes') and (content.replace(self.changedStr,self.modifyStr),1) :
                            if not self.replaceFile(pathToFile,True) :
                                print(path+'替换文件数据失败!')
                                allChanged = False
                            else :
                                print(path + '重置成功!')
                                break
                        elif (inputStr=='no') :
                            print(path+' 节点已修改,放弃重置')
                            break
                # 找不到
                elif (content.count(self.modifyStr)<1) :
                    print (path +' 文件中未发现替换节点字符串!')
                    allChanged = False
                # 多次出现
                elif (content.count(self.modifyStr) > 1) :
                    print (path+' 文件中异常出现%s次节点字符串!'%(content.count(self.modifyStr)))
                    # print(re.findall(self.changeStart,content))
                    allChanged = False
                else :
                    allChanged = False
                    print(path+'修改失败!')
            originFile.close()
            if allChanged == False :
                return False        
        return allChanged

    # 替换指定文件数据
    def replaceFile(self,pathToFile,reSet=False) :
        print('开始替换文件!')
        if not os.path.exists(pathToFile) :
            print('未找到文件: '+pathToFile)
            return False

        path = pathToFile.split(self.replaceFileName,1)[0]
        backFilePath = path + self.replaceFileBackName
        if os.path.exists(backFilePath) :
            print('文件已备份!')
            print(backFilePath)
        else :
            try :
                # 文件复制备份
                shutil.copy(pathToFile,backFilePath)
                print('备份文件成功!')
                print(backFilePath)
            except Exception as e :
                print('备份文件失败!',e)
                return False

        # 删除原文件
        # print('开始删除文件: '+pathToFile)
        # try :
        #     os.remove(pathToFile)
        #     print('源文件已删除')
        # except Exception as e :
        #     print('删除源文件失败!',e)
        #     return False
        
        # 替换文件
        if reSet == True :
            if path.find('dota_schinese') > 1 :
                dirName = 'dota_schinese'
            else :
                dirName = 'dota'

            replacePath = path+'/'+self.replaceFileBackName            

        else :  
            if path.find('dota_schinese') > 1 :
                dirName = 'dota_schinese'
            else :
                dirName = 'dota'

            replacePath = 'replace_file/%s/'%(dirName)+self.replaceFileName

        try :
            shutil.copy(replacePath,pathToFile)
            print('替换文件成功',dirName+'/'+self.replaceFileName)
            return True
        except Exception as e :
            print('替换文件: %s 失败'%(replacePath),e)
            return False

        

        # if not os.path.exists(fileToPath) :
        #     print('未发现修改文件')
        #     return False
        # try:
        #     fileObj = open(fileToPath,'r+',encoding='utf-8',errors='ignore')
        # except Exception as e :
        #     print('修改文件打开失败!',e)
        #     return False
        # try :
        #     fileObj.seek(1)
        #     fileObj.truncate()
        #     fileObj.write(newData)
        #     return True
        # except Exception as e :
        #     print('替换文件数据失败!',e)
        #     # 回滚数据
        #     return False
        # else :
        #     fileObj.close()


        
    #移动配音文件夹 
    def remove_file(self) :
        path = self.gamePath+'/'+self.moveFilePath
        pathToFile = self.gamePath+'/'+self.moveFilePath+'/'+self.moveFile
        copyFile = self.moveFile+'.zip'

        # 替换文件检查
        if not os.path.exists(copyFile) :
            print('替换文件丢失!')
            return False

        # 检查文件路径/文件是否存在
        if os.path.exists(pathToFile) :
            print('配音文件已存在!无需移动')
            return True
        # 创建路径 移动文件
        elif not os.path.exists(path):
            print('未发现路径:%s'%(self.moveFilePath))
            print('开始创建目录%s'%(self.moveFile))
            try :
                os.makedirs(path)
                print('成功创建路径')
            except Exception as e :
                print('创建路径失败',e)
                return False

        print('开始移动压缩文件!')
        try :
            zip = zipfile.ZipFile(copyFile)
            zip.extractall(path)
            print('解压移动文件成功!')
            return True
        except Exception as e :
            print('解压移动文件失败!',e)
            return False

    # 创建未发现列表中的路径
    def createDirs(self,dirs) :
        for i in range(len(dirs)) :
            path = self.gamePath+'/'+dirs[i]
            print('开始创建目录: %s'%(path))
            try:
                os.makedirs(path)
            except Exception as e :
                print(e)
                print('创建失败!请手动创建...')
                return False
            else :
                print('创建成功 : '+path)
        return True

ChangeDota2Sound().changeStart()

