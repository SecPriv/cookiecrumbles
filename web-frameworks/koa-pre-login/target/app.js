const Koa = require('koa');
const Router = require('@koa/router');

const app = new Koa();
const router = new Router()

const crypto = require("crypto");
app.keys = [crypto.randomBytes(256)];
const session = require('koa-session');
app.use(session(app));

const bodyParser = require('koa-bodyparser');
app.use(bodyParser());

const render = require('koa-ejs');
const path = require('path');
render(app, {
    root: path.join(__dirname, 'views'),
    layout: false,
});


const passport = require('koa-passport');
const LocalStrategy = require('passport-local').Strategy;

app.use(passport.initialize());
app.use(passport.session());
passport.serializeUser((user, done) => { done(null, user); });
passport.deserializeUser((user, done) => { done(null, user); });
passport.use(new LocalStrategy( (username, password, done) => {
    if(password === username && username in balance){
        return done(null, username);
    } else {
        return done(null, false);
    }
}));


const csrf = require('koa-csrf');
const csrfProtection = new csrf();

// methods to be excluded from CSRF protection
const excludeCSRF = [ '/login' ];

app.use((ctx, next) => {
  if (excludeCSRF.includes(ctx.request.url)) {
    return next();
  }
  return csrfProtection(ctx, next);
})


app.use(router.routes());


// USERS
var balance = { 
    alice: 1000,
    bob: 1000,
    john_doe: 1000,
    attacker: 1000 
  };


////

router.get('root', '/', (ctx) => {
    return ctx.render('index', {
        authenticated: ctx.isAuthenticated(),
        user: ctx.state.user,
        balance: balance[ctx.state.user],
        debug_sessionID: "",
        debug_csrf_secret: ctx.session.secret,
        // 3.0.8
        csrf_token: ctx.csrf,
    });
});


router.get('/login', async (ctx) => {
    if (!ctx.isAuthenticated()) { 
        return ctx.render("login", {
            debug_sessionID: "",
            debug_csrf_secret: ctx.session.secret,
            csrf_token: ""

        });        
    } else {
        ctx.redirect('/');
    }
});


router.post('/login', passport.authenticate('local', {
    successRedirect: '/',
    failureRedirect: '/login',
}));


router.post('/transfer', async (ctx) => {
    if( !(ctx.isAuthenticated())){
        ctx.body = "Please login first.";
    } else if( !(ctx.request.body.target in balance)) {
        ctx.body = "User " + ctx.request.body.target + " does not exist.";
    } else {
        balance[ctx.request.body.target] += parseInt(ctx.request.body.ammount);
        balance[ctx.state.user] -= parseInt(ctx.request.body.ammount);
        console.log("Executing Trasfer\n" + ctx.request.body.ammount + " from " + ctx.state.user + " to " + ctx.request.body.target);
        ctx.body = "Successfull transferred " + ctx.request.body.ammount + " from " + ctx.state.user + " to " + ctx.request.body.target;
    }
})


router.get('/logout', async (ctx) => {
    if (ctx.isAuthenticated()) {
        ctx.logout();
    }
    ctx.redirect('/');
});


app.listen(3000);
