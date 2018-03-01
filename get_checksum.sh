for i in $*
do
    echo "Scanning $i"
    find Media/$i -type f -exec sha1sum {} \; >> ${i}_sums.txt 2>&1
done
