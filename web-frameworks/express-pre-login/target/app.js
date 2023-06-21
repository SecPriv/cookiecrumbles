const express = require('express');
const app = express();
app.use(express.urlencoded({extended: true}));
app.set('view engine', 'ejs');


const session = require('express-session');
var crypto = require("crypto");
app.use(session({
    secret: crypto.randomBytes(20).toString('hex'),
    resave: true,
    saveUninitialized: true}));

// To prevent session fixation@0.5.3
var fixation = require('express-session-fixation');
app.use(fixation({}));


const passport = require('passport');
const LocalStrategy = require('passport-local').Strategy;

app.use(passport.initialize());
app.use(passport.session());
passport.serializeUser(function (user, done) { done(null, user); });
passport.deserializeUser(function (user, done) { done(null, user) });
passport.use(
    new LocalStrategy((username, password, done) => {
        if(password === username && username in balance){
            return done(null, username);
        }
        return done(null, false);
    })
)


const csrf = require('csurf')
const csrfProtection = csrf();


// USERS
var balance = { 
       alice: 1000,
       bob: 1000,
       john_doe: 1000,
       attacker: 1000 
     };


////

app.get('/', csrfProtection, (req, res) => {
    res.render('index', {
        authenticated: req.isAuthenticated(),
        user: req.user,
        balance: balance[req.user],
        debug_sessionID: req.sessionID,
        debug_csrf_secret: req.session.csrfSecret,
        csrf_token: req.csrfToken()
    });
})

app.get('/login', (req, res) => {
    res.render('login', {
        debug_sessionID: req.sessionID,
        debug_csrf_secret: req.session.csrfSecret,
        csrf_token: ""
    });
})

app.post('/login', (req, res, next) => {
    // To prevent session fixation@0.5.3
    req.resetSessionID().then(function() {
        passport.authenticate('local',{
            successRedirect: '/',
            failureRedirect: '/login',
        })(req,res,next);
    })
})

app.post('/transfer', csrfProtection, (req, res, next) => {
    if( !(req.isAuthenticated())){
        res.send("Please login first.");
    } else if( !(req.body.target in balance)) {
        res.send("User " + req.body.target + " does not exist.");
    } else {
        balance[req.body.target] += parseInt(req.body.ammount);
        balance[req.user] -= parseInt(req.body.ammount);
        console.log("Executing Trasfer\n" + req.body.ammount + " from " + req.user + " to " + req.body.target);
        res.send("Successfull transferred " + req.body.ammount + " from " + req.user + " to " + req.body.target);
    }
})

app.get('/logout', (req, res, next) => {
    req.logout(function(err) {
        if (err) { return next(err); }
        res.redirect('/');
      });
    req.session.destroy();
    res.redirect('/');
})

app.listen(3000);
