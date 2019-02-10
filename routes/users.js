var express = require('express');
var router = express.Router();
var config = require('../config')();
var mailgun = require('mailgun-js')({apiKey: config.MAILGUN_KEY, domain: config.mailgun_domain});
var url = require('url')

function querify(path, query) {
  return url.format({
    pathname: path,
    query: query})
}

/* GET users listing. */
router.get('/', function(req, res) {
  res.send('respond with a resource');
});

router.get('/subscribe', function(req, res) {
  res.render('subscribe')
});

router.post('/subscribe', function(req, res) {
  console.log('subscribing ' + req.body.email)

  var confirmLink = config.protocol + "://" + config.host + "/users/confirm/" + encodeURIComponent(req.body.email)
  data = {
    from: "zeb@sandbox47c93c3b2e5a409c96663306a9320d6f.mailgun.org",
    to: req.body.email,
    subject: "Confirm Your Subscription",
    text: "To confirm your subscription, paste this link into your browser: " + confirmLink,
    html: "To confirm your subscription, please click this link <a href='" + confirmLink + "'>" + confirmLink + "</a>"
  }

  mailgun.messages().send(data, function(err, body) {
    if(err) {
      console.log(err)
      res.render('error', {err: err, message: "Sorry, we weren't able to send you a confirmation email. Maybe try a different email address."})
    } else {
      res.redirect(querify('/', {'flash': 'Almost done! Check your email to confirm your subscription!'}))
    }
  })
});

router.get('/confirm/:email', function(req, res) {

  var createData = {
    'subscribed': true,
    'address': req.params.email,
    'name': req.params.email,
    'vars': {}
  }

  console.log(JSON.stringify(createData))
  mailgun.lists(config.mailgun_list).members().create(createData, function(err, data) {
    if(err) {
      console.log(err)
      res.render('error', {err: err, message: "Oops, looks like you're already subscribed!"})
    } else {
      res.redirect(querify('/', {'flash': 'Subscribed, thank you!'}))
    }
  })
});

module.exports = router;
