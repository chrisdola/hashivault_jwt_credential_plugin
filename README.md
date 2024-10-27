# HashiCorp Vault JWT Credential Plugin

This AAP plugin is intended to allow a credential attached to a job to assume a HashiVault Role using JWT Auth.

---

**_NOTE BEFORE INSTALLING THIS PLUGIN_**

This plugin uses the jwt python module which can use a newer version of cryptography than the openssl version that is currently installed in your Tower venv. There are some instances where this causes the cryptogrphay module to update past a version that the installed openssl version supports.

It is _strongly_ advised to check wither your venv is using at least pyopenssl 22.0.0 or later and upgrade to at least this version if necessary.

---

To install the plugin:

1.  Copy the files from this repo onto the AAP controller nodes.
2.  From a terminal session on each AAP controller node, cd to the folder you've copied the code to.
3.  Install the Python code in the AAP virtualenv on _each_ controller node:

```shell
awx-python -m pip install .
```

4.  From _any_ AAP controller node, run this command to register the plugin:

```shell
awx-manage setup_managed_credential_types
```

5.  Restart the AAP services:

```shell
automation-controller-service restart
```
