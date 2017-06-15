# do-audit
Audit your Digital Ocean account and make sure you know what's up.

The script can currently list your droplets and domains with their basic
information, and has a `ping-domains` command which tries to send a test
request to all your domains and checks the response for you.

## Installation
From PyPI (recommended):

```
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
or pass it explicitly (`do-audit -t '...'`).
Everything else should be pretty straightforward:

```
$ do-audit --help 
Usage: do-audit [OPTIONS] COMMAND [ARGS]...

  Simple command line interface for doing an audit of your Digital Ocean
  account and making sure you know what's up.

  See https://github.com/omni-digital/do-audit for more info.

Options:
  -t, --access-token TEXT  Digital Ocean API access token.
  --help                   Show this message and exit.

Commands:
  account       Show basic account info
  domains       List your domains
  droplets      List your droplets
  ping-domains  Ping your domains and see what's the response
```

## Tests
Package was tested with the help of `py.test` and `tox` on Python 2.7, 3.4, 3.5
and 3.6 (see `tox.ini`).

To run tests yourself you need to set an environment variable with Digital Ocean
access token before running `tox` inside the repository:

```shell
$ export DO_ACCESS_TOKEN='...'
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
