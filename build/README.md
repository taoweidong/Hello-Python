# 打包说明

本项目使用PyInstaller将Python脚本打包成独立的可执行文件。

## Windows平台打包

在Windows平台上，运行以下脚本进行打包：

```
build\build_windows_fixed.bat
```

打包生成的可执行文件将位于：
1. `build\dist\click_demo.exe`（构建过程中的临时位置）
2. `dist\click_demo.exe`（最终归档位置，位于项目根目录下）

## Linux平台打包

在Linux平台上，运行以下脚本进行打包：

```
build/build_linux.sh
```

打包生成的可执行文件将位于：
1. `build/dist/click_demo`（构建过程中的临时位置）
2. `dist/click_demo`（最终归档位置，位于项目根目录下）

## 打包过程

1. 脚本会自动创建临时工作目录
2. 使用PyInstaller进行打包
3. 清理临时文件
4. 将最终的可执行文件放置在项目根目录下的 `dist/` 目录中

## 注意事项

- 确保已安装PyInstaller: `pip install pyinstaller`
- 打包过程可能需要几分钟时间
- 所有过程文件都会保存在build目录下，不会污染项目根目录
- 脚本会自动处理路径问题，确保在不同环境中都能正常工作
- 生成的可执行文件会被自动归档到项目根目录下的dist目录中
- 修复了中文控制台乱码问题和打包后依赖导入问题