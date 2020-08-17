# pil
Koa middleware for setting rules HTTP method parameters to endpoints.
Make parameter validation as easy-as-pil

`npm install pil`

<img src="media/redpillbluepill.png"><br>


### pil.set({opts})

Set parameter options;

| Key | Type | Description |
| --- | --- | --- |
| name | String | Name of your parameter, you must include this in your options. |
| required | Boolean | Required if true, optional if false - true by default. |
| regex | Object (regex) | A regular expression to match with if parameter is string. |
| type | String | Parameter data type; boolean - number - string - object - array. |
| error | Object | Set custom error messages in specific scenarios. |

## Quickstart

Here is an example application using pil to set parameters we want, we can be sure we will receive parameters in `request.params` as pil handles everything else.

```javascript
'use strict';

let koa = require('koa'),
    mount = require('koa-mount'),
    Router = require('koa-router'),
    bodyParser = require('koa-bodyparser'),
    pil = require('pil'),
    app = koa()

app.use(bodyParser())

let test = new Router()

app.use(mount('/', test.middleware()))

test.get('/get',
    pil.set([
        {
            name: "foo",
            required: true,
            type: "string",
            error: {
                missing: "You need to provide foo otherwise the world will break"
            }
        },{
            name: "email",
            regex: /@/g
        }]),
function * () {
    let foo = this.request.params.foo,
        email = this.request.params.email

    this.body = "hello world"
})

app.listen(3001)
```

Check examples in *test/* folder in both *app.js* for pure koa application using pil or *rapp.js* for routed app example like this quickstart.

* Must be running node with `v4.3.*` or higher

* For POST / PUT methods pil works with works with the official `koa-bodyparser` best or other body parsing libraries which set data to `this.request.body`. This libraries will extend to support pure koa post requests.

Authors;
[Ulpian Morina](https://github.com/ulpian)
