--- app.js	2023-06-18 22:00:48
+++ app-0.6.0-keepSessionInfo.js	2023-06-18 22:01:03
@@ -63,10 +63,11 @@
 })
 
 app.post('/login', (req, res, next) => {
-    // To simulate session-fixation@0.5.3
+    // Usage with 0.6.0
     passport.authenticate('local',{
         successRedirect: '/',
         failureRedirect: '/login',
+        keepSessionInfo: true
     })(req,res,next);
 })
 
@@ -88,8 +89,8 @@
         if (err) { return next(err); }
         res.redirect('/');
       });
-    req.session.destroy();
-    res.redirect('/');
+    // req.session.destroy();
+    // res.redirect('/');
 })
 
 app.listen(3000);
