DATE="$(date +%Y-%m-%d_%H.%m.%s)"
mv production.yml production_"$DATE".yml
wget https://github.com/jueves/NL_to_table/raw/main/docker/production.yml
