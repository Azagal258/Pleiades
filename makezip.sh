#! /bin/bash

Check_files() {
    local res_array=()
    local dir="$1"
    # Ensure empty * ops unpack as nothing
    shopt -s nullglob
    for subdir in "$dir"/*; do
        # Check if dir
        if [[ -d "$subdir" ]]; then
            for image in "$subdir"/* ; do
                res_array+=("$image")
            done
        fi
    done
    # Disable nullglob for safety"
    shopt -u nullglob
    printf "%s\n" "${res_array[@]}"
}

Date_request() {
    local out="False"
    until [ $out == "True" ]; do
        echo "From what date to zip from? aaaa-mm-dd" >&2
        read -r datevar
        # Ensure ISO-8601 compliance
        if [[ $datevar =~ ^([0-9]{4})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$ ]]; then
            out="True"
        else
            echo "Date or format is invalid" >&2
        fi
    done
    echo "$datevar"
}

Check_metadata() {
    local utime
    utime="$(stat -c %y "$1" | cut -d ' ' -f1)"
    echo "$utime"
}

echo "What group do you want to zip from (artms/tripleS/idntt)"
# TODO : add check for valid group
read -r groupvar

# mapfile -t file_array < <(Check_files "$groupvar")
mapfile -t file_array < <(find "$groupvar" -mindepth 2 -maxdepth 2 -type f)
date_from="$(Date_request)"
current_date="$(date -I)"

zip_array=()
for f in "${file_array[@]}"; do
    utime="$(Check_metadata "$f")"
    if [[ "$utime" > "$date_from" ]]; then
        zip_array+=("$f")
    fi
done
mkdir Archives
zip ./Archives/"$groupvar"-"$date_from"-to-"$current_date".zip -r "${zip_array[@]}"