# Dependencies 
## dice class
- numpy 2.1.3

## unit tests
- rich 13.8.1

# To-Do
- Make more unit tests
  - Statistical check, use advantage counting formulae to verify dice roller is producing statistically accurate results.
  - Error interceptor, make it so that if an error is raised in a mass test, you get the random seed and input.
- Add to Pypi.
- Implementing kwargs has caused some headaches, I should probably handle making sure that the dice dict has only exactly the information needed for its chosen roller in a more systematic way. Maybe with a function that compares the dice dict's parameters with the chosen roller's expected parameters, and trims out the parameters we don't need.
- Make the optional argument load random state actually do something.