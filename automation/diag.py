from automation.adb_utils import run_adb

print('--- Magisk service.d ---')
print(run_adb('ls -la /data/adb/service.d/', is_su=True))

print('--- ps -ef ---')
out = run_adb('ps -ef', is_su=True)
for line in out.splitlines():
    if any(k in line for k in ['daemon', 'vpn', 'urban', '94-', '98-', 'toki', 'magisk']):
        print(line)
