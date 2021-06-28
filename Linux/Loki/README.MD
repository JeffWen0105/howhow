# 自動化建置 Loki 的代理採集工具 Promtail

#### 1. 執行需求：

```
本專案僅支援 AMD 64， 如您的電腦指令集為 ARM 64，請更換 Promtail 程式
不知道怎麼檢查，請使用指令 uname -a ，僅限 UNIX 家族
```

#### 2. 使用方式：

```
1. 輸入： mkdir -p ~/howhowwen/Loki && cd ~/howhowwen/Loki &&  curl https://jeffwen0105.github.io/howhow/Linux/Loki/script/loki_promtail.sh --output loki_promtail.sh  && sh loki_promtail.sh
2. 下載完畢後修改 promatil內的 conf 設定檔，內有詳細說明
3. 執行: sh start_promtail.sh 就會開始發送數據
```

