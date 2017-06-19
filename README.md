# do-audit
Audit your Digital Ocean account and make sure you know what's up.

The script can currently list your droplets and domains with their basic
information, and has a `ping-domains` command which tries to send a test
request to all your domains and checks the response for you.

## Installation
From PyPI (recommended):

```shell
$ pip install do-audit
```

With `git clone`:

```shell
$ git clone https://github.com/omni-digital/do-audit
$ pip install -r do-audit/requirements.txt
$ cd do-audit/bin
```

## Usage
To use the script you'll need Digital Ocean [access token][do access token]
and either save it as an environment variable (`$ export DO_ACCESS_TOKEN='...'`)
or pass it explicitly (`do-audit -t '...'`) with each command.
Everything else should be pretty straightforward:

```shell
$ do-audit --help 
Usage: do-audit [OPTIONS] COMMAND [ARGS]...

  Simple command line interface for doing an audit of your Digital Ocean
  account and making sure you know what's up.

  See https://github.com/omni-digital/do-audit for more info.

Options:
  -t, --access-token TEXT         Digital Ocean API access token.
  -o, --output-file FILENAME      Output file path.
  -f, --data-format [json|xls|yaml|csv|dbf|tsv|html|latex|xlsx|ods]
                                  Output file dat format.
  -v, --verbose                   Show extra information.
  --help                          Show this message and exit.

Commands:
  account       Show basic account info
  domains       List your domains
  droplets      List your droplets
  ping-domains  Ping your domains and see what's the response
```

## Examples
The script has four subcommands, all with the same available options:

```shell
$ do-audit account
Email:              user@example.com
Status:             active
Droplet limit:      25
```

Each command has a `--verbose` option that shows more information:

```shell
$ do-audit account -v
Email:              user@example.com
Status:             active
Droplet limit:      25
Floating IP limit:  3
UUID:               uuid
```

Both `domains` and `droplets` subcommands work the same way:

```shell
$ do-audit droplets
# ubuntu-512mb-lon1-01 (active)
OS:                 Ubuntu 16.04.2x 64
IP:                 192.168.1.0
CPU:                1
Memory:             512 MB
Disk:               20 GB
URL:                https://cloud.digitalocean.com/droplets/2/graphs
Created at:         Mon, 05/08/17 12:52:22

$ do-audit domains
# example.com
@                                   A          192.168.0.1
blog                                A          192.168.0.1

# example.co.uk
@                                   A          192.168.0.2
www                                 A          192.168.0.2
```

All commands can be exported to a file:

```shell
$ do-audit account -o account.csv
CSV data was successfully exported to 'account.csv'

$ cat account.csv
Email,Status,Droplet limit
user@example.com,active,25

$ do-audit droplets -o droplets.csv -f json
JSON data was successfully exported to 'droplets.csv'
```

## Tests
Package was tested with the help of `py.test` and `tox` on Python 2.7, 3.4, 3.5
and 3.6 (see `tox.ini`).

To run tests yourself you need to run `tox` inside the repository:

```shell
$ pip install tox
$ tox
```

## Contributions
Package source code is available at [GitHub][github].

Feel free to use, ask, fork, star, report bugs, fix them, suggest enhancements,
add functionality and point out any mistakes. Thanks!

## Authors
Developed and maintained by [Omni Digital][omni digital].

Released under [MIT License][license].


[github]: https://github.com/omni-digital/do-audit
[license]: https://github.com/omni-digital/do-audit/blob/master/LICENSE
[omni digital]: https://omni-digital.co.uk/
[do access token]: https://www.digitalocean.com/community/tutorials/how-to-use-the-digitalocean-api-v2#how-to-generate-a-personal-access-token
