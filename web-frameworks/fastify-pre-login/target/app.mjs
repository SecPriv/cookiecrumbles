import Fastify from 'fastify'
import fastifyCookie from '@fastify/cookie'
import fastifyCsrfProtection from "@fastify/csrf-protection"
import fastifyView from "@fastify/view"

import ejs from "ejs"
import fs from "fs"
import path from "path"
import crypto from "crypto"
import formbody from "@fastify/formbody"


const fastify = Fastify({ logger: true })

fastify.register(fastifyView, {
  engine: { ejs: ejs },
});
fastify.register(formbody);




import { Authenticator } from '@fastify/passport'

const fastifyPassport = new Authenticator({ 
  // // this semantics only works for @fastify/secure-session
  // clearSessionOnLogin: true, 
  // clearSessionIgnoreFields: ['passport', 'session', '_csrf'] 
})



// // CSRF-OPTION: Use with @fastify/session

fastify.register(fastifyCookie, { secret : crypto.randomBytes(20).toString('hex') }) // for cookies signature

import fastifySession from '@fastify/session'
await fastify.register(fastifyCsrfProtection, { 
    sessionPlugin: '@fastify/session',
    // getUserInfo (req) { return  req.user ?? "default" },
})


// PASSPORT-OPTION: use with @fastify/session

await fastify.register(fastifySession, {
  cookieName: 'session',
  secret: crypto.randomBytes(20).toString('hex'),
  cookie: { secure: false },
  expires: 1800000
})

////////


// // CSRF-OPTION: Use with @fastify/secure-session
// import fastifySecureSession from '@fastify/secure-session'
// await fastify.register(fastifyCsrfProtection, { 
//     sessionPlugin: '@fastify/secure-session',
//     // getUserInfo (req) { return  req.user ?? "default" },
// })


// // PASSPORT-OPTION: use with @fastify/secure-session

// await fastify.register(fastifySecureSession, { 
//   key: fs.readFileSync(path.join('/usr/src/', 'secret-key'))
// })


////////


await fastify.register(fastifyPassport.initialize())
await fastify.register(fastifyPassport.secureSession())


////////////////// STATEGIES //////////////////

import passportLocal from 'passport-local'

const LocalStrategy = passportLocal.Strategy;

fastifyPassport.use('local',
  new LocalStrategy((username, password, done) => {
    if(password === username && username in balance){
          return done(null, username);
      }
      return done(null, false);
  })
)

fastifyPassport.registerUserSerializer(async (user, request) => { console.log("LOGIN USER:" + user); return user; } );
fastifyPassport.registerUserDeserializer(async (user, request) => { return user; });

////////////////// END PASSPORT OPTIONS //////////////////


// USERS
var balance = { 
  alice: 1000,
  bob: 1000,
  john_doe: 1000,
  attacker: 1000 
};



fastify.route({
    method: 'GET',
    url: '/',
    handler: async (req, reply) => {

      // // To use userInfo
      // const token = await reply.generateCsrf( { userInfo: req.user ?? "default" })
      
      // To disable userInfo
      const token = await reply.generateCsrf()

      return reply.view("/views/index.ejs", {
        authenticated: req.isAuthenticated(),
        user: req.user,
        balance: balance[req.user],
        debug_sessionID: req.cookies.session,        // for passport-session/passport-secure-session
        debug_csrf_secret: req.session._csrf,        // for CSRF-session/CSRF-secure-session
        csrf_token: token,
        })
    }
})


fastify.route({
  method: 'GET',
  url: '/login',
  handler: async (req, reply) => {
    return reply.view("/views/login.ejs", {
      debug_sessionID: req.cookies.session,
      debug_csrf_secret: req.session._csrf,        // for CSRF-session/CSRF-secure-session
      csrf_token: ""
    })
  }
})


fastify.post('/login',
    { preValidation: fastifyPassport.authenticate('local', { successRedirect: '/', failureRedirect: '/login', authInfo: false, clearSessionOnLogin: false, 
    clearSessionIgnoreFields: ['passport', 'session', '_csrf', 'test']  }) },
    (req, res, next) => {
    fastifyPassport.authenticate('local',{
          successRedirect : '/',
          failureRedirect : '/login',
          clearSessionOnLogin: false, 
  clearSessionIgnoreFields: ['passport', 'session', '_csrf'] 
      })(req,res,next);
})


fastify.post(
  '/transfer',
  {
    preHandler: fastify.csrfProtection
  },
  async (req, reply) => {
    if( !(req.isAuthenticated())){
        return "Please login first.";
    } else if( !(req.body.target in balance)) {
        return "User " + req.body.target + " does not exist.";
    } else {
        balance[req.body.target] += parseInt(req.body.ammount);
        balance[req.user] -= parseInt(req.body.ammount);
        console.log("Executing Trasfer\n" + req.body.ammount + " from " + req.user + " to " + req.body.target);
        return "Successfull transferred " + req.body.ammount + " from " + req.user + " to " + req.body.target;
    }
  }
)


fastify.get('/logout', (request, reply) => {
    if (request.isAuthenticated())
      request.logOut();
    return reply.redirect('/')
  });


fastify.listen({ port: 3000, host : '0.0.0.0' }, function (err, address) {
  if (err) {
    fastify.log.error(err)
    process.exit(1)
  }
})
