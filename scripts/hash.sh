DATA="/home/yuehang/pythonProject/VK-GPU/static/api/esolation/hash.json"

funecho() {
  echo '{
        "data": ['$1', '$2', '$3', '$4', '$5', '$6']
      }' >$DATA
}

sleep 2
funecho 10 0 0 0 0 0
sleep 2
funecho 10 9 0 0 0 0
sleep 2
funecho 10 9 11 0 0 0
sleep 2
funecho 10 9 11 15 0 0
sleep 2
funecho 10 9 11 15 12 0
sleep 2
funecho 10 9 11 15 12 16