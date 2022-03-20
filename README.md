# flaked
`flaked` 构建于 `flake8` 之上，增加了对 `mako` 文件中 python 代码的检查，以及某些实用的功能。

## 快速开始
```shell
> pip install flaked

> flaked <some_mako_file>
```
由于 `flaked` 是在 `flake8` 之上的封装，所以使用方式与 `flake8` 如出一辙。


## Change Log

- v0.1.0: 增加对 `mako` 文件的基础检查。
- v0.2.0: 增加 `flaked-shire` 插件（for douban), 检查 shire 老代码。
