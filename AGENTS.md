

# Rule
任何修改, 默认动作都是 更新版本号(小版本递增) + 推送git

## 禁止修改文件列表, 改为提示
.env
.env.example

**提交格式：** `<type>: <description>` 
    — 类型：feat, fix, refactor, docs, test, chore, perf,ci
    - 描述: 使用中文

## 开发文档中心原则
对外材料统一放 docs/prod
开发过程记录文档 docs/dev/
文档采用索引文件 + 细节文件的架构进行组织维护