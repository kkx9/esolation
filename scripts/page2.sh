DATA="/home/yuehang/pythonProject/VK-GPU/static/api/esolation/page2.json"

funecho() {
  echo '{
        "data": ['$1', '$2', '$3', '$4', '$5']
      }' >$DATA
}

sleep 2
funecho 1 0 0 0 0
sleep 2
funecho "0.5" "0.5" 0 0 0
sleep 2
funecho "0.33" "0.33" "0.33" 0 0
sleep 2
funecho "0.25" "0.25" "0.25" "0.25" 0
sleep 2
funecho "0.2" "0.2" "0.2" "0.2" "0.2"
