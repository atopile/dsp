# Setup

```bash
# rsync nonos_server to nonos
rsync -a dsp_server nonos:
ssh <pi_hostname> "cd dsp_server && ./setup.sh"
```

## Bluetooth

Enable `FastConnectable=y` in `/etc/bluetooth/main.conf`
Make pairable and trust all devices:

Not sure about those:

```
[General]
AutoEnable=true
Class = 0x200414
DiscoverableTimeout = 0
PairableTimeout = 0
JustWorksRepairing = always
```

# Broken

- bluetooth only works after login with ssh
- vnc stuff, see setup.sh (needs manual vncpasswd set)

