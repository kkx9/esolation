DATA="/home/yuehang/pythonProject/VK-GPU/static/api/gpu/put_image.json"

funecho() {
  echo '{
        "data": ['$1', '$2', '$3', '$4']
      }' >$DATA
}

sleep 2
funecho 124 0 0 0
sleep 2
funecho 124 149 0 0
sleep 2
funecho 124 149 739 0
sleep 2
funecho 124 149 739 1204