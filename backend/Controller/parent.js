import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import verifyEmail from "./VerifyEmail.js";
import Parent from "../Model/Parent.js";
import Children from "../Model/children.js";

export const signIn = async (req, res) => {
    const { email, password } = req.body;
    try {
        await Parent.findOne({ email }).then(async (_user) => {
            if (_user) {
                const isPasswordCorrect = await bcrypt.compare(password, _user.password)
                if (isPasswordCorrect) {
                    const token = jwt.sign({ email, id: _user.id }, process.env.SECRET, { expiresIn: '24h' })
                    return res.status(203).json({ user: _user, token })
                } else {
                    return res.status(402).json({ message: "Incorrect Password" })
                }
            } else {
                return res.status(402).json({ message: "User not found" })
            }
        })
    } catch (error) {
        return res.status(403).json(error)
    }
}


export const signUp = async (req, res) => {

    const { firstName, lastName, email, password, confirmPassword } = req.body;
    try {
        // const validate = await verifyEmail(email);
        if (true) {
            await Parent.findOne({ email }).then(async (_user) => {
                if (_user) {
                    return res.status(403).json("User with EmailId already exist")
                } else {
                    if (password !== confirmPassword) {
                        return res.status(403).json({ message: "Passwords does not match" })
                    }


                    const hashedPassword = await bcrypt.hash(password, 12);
                    const newUser = new Parent({ email, firstName, lastName, password: hashedPassword })
                    await newUser.save();
                    const token = jwt.sign({ email, id: newUser._id }, process.env.SECRET, { expiresIn: "24h" })
                    return res.status(200).json({ user: newUser, token })
                }
            })
        } else {
            return res.status(403).json({ message: "Please enter a valid email" })
        }
    } catch (error) {
        console.log(error)
        return res.status(403).json(error)
    }
}


export const addChildren = async (req, res) => {

    const data = req.body;

    // Only for testing purpose
    data.contentFiltering = JSON.parse(data.contentFiltering);
    data.blockedWebsites = JSON.parse(data.blockedWebsites);
    try {

        let access_token = req.headers['authorization'];
        let access = access_token.split(' ')[1];
        let payload = jwt.verify(access, process.env.SECRET);
        const parent_email = payload.email;
        await Parent.findOne({ email: parent_email }).then(async (_parent) => {
            data["parent"] = _parent._id;
            const newChildren = new Children(data);
            await newChildren.save();
            await Children.findByIdAndUpdate(newChildren._id, { token: newChildren._id }, { new: true })

            let childList = _parent.childrens;
            childList.push(newChildren._id);
            await Parent.findOneAndUpdate({ email: parent_email }, { childrens: childList }, { new: true }).then((__parent) => {
                return res.status(203).json(__parent);
            })
        })
    } catch (error) {
        console.log(error)
        return res.status(403).json(error)
    }

}