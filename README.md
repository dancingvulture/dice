# Dependencies 
## dice class
- numpy 2.1.3

## unit tests
- rich 13.8.1

# To-Do
- Make more unit tests
  - Random dice input maker (make sure to also make kwargs).
  - Statistical check, use advantage counting formulae to verify dice roller is producing statistically accurate results.
  - Error interceptor, make it so that if an error is raised in a mass test, you get the random seed and input.
- Add random seed option
- Make `__init__` easier to maintain, maybe by having it auto-pull settings options and defaults from somewhere.
- Add to Pypi.
- Fix the way tests interact with the roller (should import dice and use the interface in `__init__`).
- Figure out if having `main` makes sense.
- 
