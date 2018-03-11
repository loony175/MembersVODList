SNH48 Group所有能获取到的成员录播

## Requirement
```
sudo apt update && sudo apt install -y jq
```

## Usage & Updating manually
工作原理：执行`./bash/koudai48`后，首先向口袋API发送POST请求以获取完整的成员录播列表（JSON格式），剔除一些我至今没发现有什么用的参数，然后以特定的memberId值为条件过滤出单个成员的所有录播，并写入normal文件夹下的对应文件中，最后再过滤出所有录播的开始时间和URL，并写入quiet文件夹下的对应文件中。

本repository中的录播列表我会不定期更新，如需自行手动更新，也可通过执行上述脚本实现。
