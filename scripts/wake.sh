DATA="/home/yuehang/pythonProject/VK-GPU/static/api/esolation/wake.json"

funecho() {
  echo '{
        "data": ['$1', '$2', '$3', '$4', '$5', '$6']
      }' >$DATA
}

sleep 2
funecho 2000 0 0 0 0 0
sleep 2
funecho 2000 16 0 0 0 0
sleep 2
funecho 2000 16 21 0 0 0
sleep 2
funecho 2000 16 21 18 0 0
sleep 2
funecho 2000 16 21 18 11 0
sleep 2
funecho 2000 16 21 18 11 22