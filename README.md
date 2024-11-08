# HashiCorp Vault JWT Credential Plugin

This AAP plugin is intended to allow a Tower Credential to provide a wrapped secret-id for a pre-defined role to a playbook. This is achieved by the credential plugin issuing a JWT, authenticating to Vault using the JWT auth method, and then issuing a wrapped secret-id which is made availabe within the playbook using the WRAPPED_VAULT_TOKEN env variable.

**Why use this type of credential plugin?**

"Secret-zero" is a common challenge when managing Vault AppRole credentials - how do you securely pre-seed the secret-id into a process without just storing the secret-id somewhere else? Within Tower/AAP that's a common problem one would face since all the existing solutions rely on manually storing the secret-id in a credential or even storing it within an Ansible Vault. Plus depending on the Ansible environment. Not ideal right?

This plugin attempts to create a more secure way to provide Vault credentials to a playbook by allowing Tower/AAP to act as a "trusted orchestrator" to issue Vault secrets.

**How does this plugin work?**

The basic flow is as follows:

1. On playbook execute, Tower/AAP uses the credential plugin to create a JWT.
2. The credential plugin calls Vault to login using the JWT and a specific, locked-down vault policy is attached to the token
3. The token is used to request a wrapped secret-id for the playbook's approle.
4. The wrapped token is provided to the playbook as an environment variable which the playbook can unwrap and use to authenticate to vault to retrieve any other credentials the approle has access to.

---

To-Do:

1. Add a diagram and process flow to README.
2. Add support for passing JWT signing key in a text field within the credential page in Tower.
3. Add fields for custom ttls for the JWT & wrapped token.
4. Tutorial for creating the credential in Tower, how it will be used within a playbook, and the guardrails that need to be in place to ensure the solution is secure.

---

**_NOTE BEFORE INSTALLING THIS PLUGIN_**

This plugin uses the jwt python module which can use a newer version of cryptography. There are some instances where this causes the cryptogrphay module to update past a version that the installed openssl version supports.

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
