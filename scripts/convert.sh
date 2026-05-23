if [ ! "${RESOURCE_FOLDER}" ]; then
    echo "RESOURCE_FOLDER environment variable is empty."
    exit 1
fi

for EP in "$@"
do
    python ~/code/CompareSBV/src/compare.py -o ${RESOURCE_FOLDER}/data/zhz/data/$EP.csv -f database -nd ${RESOURCE_FOLDER}/subtitles/zhz/a/$EP.sbv ${RESOURCE_FOLDER}/subtitles/zhz/b/$EP.sbv
done