--- app.js	2023-06-18 22:00:48
+++ app-0.6.0.js	2023-06-18 22:00:53
@@ -63,7 +63,7 @@
 })
 
 app.post('/login', (req, res, next) => {
-    // To simulate session-fixation@0.5.3
+    // Usage with 0.6.0
     passport.authenticate('local',{
         successRedirect: '/',
         failureRedirect: '/login',
@@ -88,8 +88,8 @@
         if (err) { return next(err); }
         res.redirect('/');
       });
-    req.session.destroy();
-    res.redirect('/');
+    // req.session.destroy();
+    // res.redirect('/');
 })
 
 app.listen(3000);
