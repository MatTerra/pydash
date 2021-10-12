#!/bin/bash
results_dir=traffic_shaping_tests
profiles=("LMH" "LLLLH" "HHHHL" "LH")

mkdir -p "$results_dir/dash_client_backup"
touch "./$results_dir/summary.txt"

backup_file="$results_dir/dash_client_backup/dash_client$(date +%H:%M:%S).json.bak"
echo -e "Backing up dash_client.json as $backup_file\n"
cp dash_client.json "$backup_file"

for profile in ${profiles[@]}; do
  echo -e "Applying profile $profile.\n"
  notify-send "Applying profile $profile."

  new_config=$(
  cat dash_client.json |\
    sed "s/\"traffic_shaping_profile_sequence\": .*,/\"traffic_shaping_profile_sequence\": \"$profile\",/"
  )
  echo "$new_config" > dash_client.json
  sleep 0.5

  python3 -u main.py | tee ./$results_dir/$profile.log
  profile_results=$(tail -n 12 ./$results_dir/$profile.log | sed '/.*Finalization/d')
  echo -e "$profile\n" >> "./$results_dir/summary.txt"
  echo -e "$profile_results" >> "./$results_dir/summary.txt"
  echo -e "=============================\n" >> "./$results_dir/summary.txt"

  echo "Testing with $profile finished!"
  notify-send "Testing with $profile finished!"
done

cp "$backup_file" dash_client.json

