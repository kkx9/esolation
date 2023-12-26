DATA="/home/yuehang/pythonProject/VK-GPU/static/api/esolation/page1.json"

funecho() {
  echo '{
        "data": ['$1', '$2', '$3', '$4', '$5']
      }' >$DATA
}

sleep 2
funecho 1 0 0 0 0