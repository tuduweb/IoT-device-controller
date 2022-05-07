#!/bin/sh
CONFIG=/boot/config.txt

## 从raspi-config中提取的代码, 需要测试
# 测试状态 raspi-config 把camera关闭

set_config_var() {
  lua - "$1" "$2" "$3" <<EOF > "$3.bak"
local key=assert(arg[1])
local value=assert(arg[2])
local fn=assert(arg[3])
local file=assert(io.open(fn))
local made_change=false
for line in file:lines() do
  if line:match("^#?%s*"..key.."=.*$") then
    line=key.."="..value
    made_change=true
  end
  print(line)
end

if not made_change then
  print(key.."="..value)
end
EOF
mv "$3.bak" "$3"
}

clear_config_var() {
  lua - "$1" "$2" <<EOF > "$2.bak"
local key=assert(arg[1])
local fn=assert(arg[2])
local file=assert(io.open(fn))
for line in file:lines() do
  if line:match("^%s*"..key.."=.*$") then
    line="#"..line
  end
  print(line)
end
EOF
mv "$2.bak" "$2"
}

get_config_var() {
  lua - "$1" "$2" <<EOF
local key=assert(arg[1])
local fn=assert(arg[2])
local file=assert(io.open(fn))
local found=false
for line in file:lines() do
  local val = line:match("^%s*"..key.."=(.*)$")
  if (val ~= nil) then
    print(val)
    found=true
    break
  end
end
if not found then
   print(0)
end
EOF
}

sed $CONFIG -i -e '/\[pi4\]/,/\[/ s/^#\?dtoverlay=vc4-f\?kms-v3d/dtoverlay=vc4-fkms-v3d/g'
sed $CONFIG -i -e '/\[pi4\]/,/\[/ !s/^dtoverlay=vc4-kms-v3d/#dtoverlay=vc4-kms-v3d/g'
sed $CONFIG -i -e '/\[pi4\]/,/\[/ !s/^dtoverlay=vc4-fkms-v3d/#dtoverlay=vc4-fkms-v3d/g'
if ! sed -n '/\[pi4\]/,/\[/ p' $CONFIG | grep -q '^dtoverlay=vc4-fkms-v3d' ; then
    if grep -q '[pi4]' $CONFIG ; then
    sed $CONFIG -i -e 's/\[pi4\]/\[pi4\]\ndtoverlay=vc4-fkms-v3d/'
    else
    printf "[pi4]\ndtoverlay=vc4-fkms-v3d\n" >> $CONFIG
    fi
fi
CUR_GPU_MEM=$(get_config_var gpu_mem $CONFIG)
if [ -z "$CUR_GPU_MEM" ] || [ "$CUR_GPU_MEM" -lt 128 ]; then
    set_config_var gpu_mem 128 $CONFIG
fi
sed $CONFIG -i -e 's/^camera_auto_detect.*/start_x=1/g'
sed $CONFIG -i -e 's/^dtoverlay=camera/#dtoverlay=camera/g'
STATUS="Legacy camera support is enabled.\n\nPlease note that this functionality is deprecated and will not be supported for future development."