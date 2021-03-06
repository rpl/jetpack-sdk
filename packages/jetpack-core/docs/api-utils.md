<!-- contributed by Drew Willcoxon [adw@mozilla.com]  -->
<!-- edited by Noelle Murata [fiveinchpixie@gmail.com]  -->

The `api-utils` module provides some helpers useful to Jetpack's high-level API
implementations.

Introduction
------------

The Jetpack high-level API design guidelines make a number of recommendations.
This module implements some of those patterns so that your own implementations
don't need to reinvent them.

For example, public constructors should be callable both with and without the
`new` keyword.  Your module can implement this recommendation using the
`publicConstructor` function.

Options objects or "dictionaries" are also common throughout the high-level
APIs.  The guidelines recommend that public constructors should generally define
a single `options` parameter rather than defining many parameters.  Since one of
Jetpack's principles is to be friendly to developers, ideally all properties on
options dictionaries should be checked for correct type, and informative error
messages should be generated when clients make mistakes.  With the
`validateOptions` function, your module can easily do so.

Functions
---------

<api name="publicConstructor">
@method
Returns a function *C* that creates an instance of `privateCtor`. *C*
may be called with or without the `new` keyword.

@returns {function}
A function that makes new instances of privateCtor.

@param [privateCtor] {constructor}
</api>

The prototype of each instance returned from *C* is *C*.`prototype`, and
*C*.`prototype` is an object whose prototype is
*`privateConstructor`*`.prototype`.  Instances returned from *C* are therefore
instances of both *C* and *`privateConstructor`*.

Additionally, the constructor of each instance returned from *C* is *C*.

Instances returned from *C* are automatically memory tracked using
`memory.track` under the bin name *`privateConstructor`*`.name`.

**Example**

    function MyObject() {}
    exports.MyObject = apiUtils.publicConstructor(MyObject);

<api name="validateOptions">
@method
@returns {object}
A validated options dictionary given some requirements. If any of the
requirements are not met, an exception is thrown.

@param [options] {object}
The options dictionary to validate.  It's not modified. If it's null or
otherwise falsey, an empty object is assumed.

@param [requirements] {object}
An object whose keys are the expected keys in *`options`*. Any key in
*`options`* that is not present in *`requirements`* is ignored.  Each
value in *`requirements`* is itself an object describing the requirements
of its key.

@prop map {function}
A function that's passed the value of the key in the *`options`*. `map`'s
return value is taken as the key's value in the final validated options,
`is`, and `ok`. If `map` throws an exception it is caught and discarded,
and the key's value is its value in `options`.

@prop is {array}
An array containing the number of `typeof` type names. If the key's value is
none of these types it fails validation. Arrays and nulls are identified by
the special type names "array" and "null"; "object" will not match either.
No type coercion is done.

@prop ok {function}
A function that is passed the key's value. If it returns false, the value
fails validation.

@prop msg {string}
If the key's value fails validation, an exception is thrown. This string
will be used as its message. If undefined, a generic message is used, unless
`is` is defined, in which case the message will state that the value needs to
be one of the given types.
</api>

`map`, `is`, and `ok` are used in that order.

The return value is an object whose keys are those keys in *`requirements`* that
are also in *`options`* and whose values are the corresponding return values of
`map` or the corresponding values in *`options`*.  Note that any keys not shared
by both *`requirements`* and *`options`* are not in the returned object.

**Examples**

A typical use:

    var opts = { foo: 1337 };
    var requirements = {
      foo: {
        map: function (val) val.toString(),
        is: ["string"],
        ok: function (val) val.length > 0,
        msg: "foo must be a non-empty string."
      }
    };
    var validatedOpts = apiUtils.validateOptions(opts, requirements);
    // validatedOpts == { foo: "1337" }

If the key `foo` is optional and doesn't need to be mapped:

    var opts = { foo: 1337 };
    var validatedOpts = apiUtils.validateOptions(opts, { foo: {} });
    // validatedOpts == { foo: 1337 }

    opts = {};
    validatedOpts = apiUtils.validateOptions(opts, { foo: {} });
    // validatedOpts == {}
