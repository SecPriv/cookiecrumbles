module.exports = {

  
  friendlyName: 'CSRF Protected action',


  description: 'Requires a CSRF token to perform the action',


  exits: {
    success: {
      viewTemplatePath: 'pages/transfer'
    }
  },


  fn: async function () {
    if(!this.req.me){
      throw new Error('Please login first.');
    }
    var currentUser = await User.findOne({ emailAddress: this.req.me.emailAddress });
    var targetUser = await User.findOne({ fullName: this.req.body.target });

    if(!currentUser) {
      throw new Error('Please login first.');
    } 
    if (!targetUser) {
      throw new Error('User ' + this.req.body.target + ' does not exist.');
    } 

    await User.updateOne({ id: targetUser.id }).set({ balance: targetUser.balance + parseInt(this.req.body.ammount) });
    await User.updateOne({ id: currentUser.id }).set({ balance: currentUser.balance - parseInt(this.req.body.ammount) });

    console.log('Executing Transfer\n' + this.req.body.ammount + ' from ' + currentUser.fullName + ' to ' + targetUser.fullName);

    return {me: this.req.me, target: targetUser, ammount: this.req.body.ammount};
  }
};
