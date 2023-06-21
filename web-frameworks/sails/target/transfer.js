module.exports = {
  friendlyName: 'CSRF Protected action',


  description: 'Requires a CSRF token to perform the action',


  exits: {
    success: {
      viewTemplatePath: 'pages/transfer'
    }
  },


  fn: async function () {
    var currentUser = await User.findOne({ emailAddress: this.req.me.emailAddress });
    var targetUser = await User.findOne({ fullName: this.req.body.target });

    if(!currentUser) {
      throw 'Please login first.';
    } 
    if (!targetUser) {
      throw 'User ' + this.req.body.target + ' does not exist.';
    } 

    await User.updateOne({ id: targetUser.id }).set({ balance: targetUser.balance + parseInt(this.req.body.ammount) });
    await User.updateOne({ id: currentUser.id }).set({ balance: currentUser.balance - parseInt(this.req.body.ammount) });

    console.log('Executing Trasfer\n' + this.req.body.ammoun + ' from ' + currentUser.fullName + ' to ' + targetUser.fullName);

    return {me: this.req.me, target: targetUser, ammount: this.req.body.ammount};
  }
};
