import emailValidator from 'deep-email-validator';

const verifyEmail = async (email) => {
    const temp = await emailValidator.validate(email)
    return temp;
}
export default verifyEmail;