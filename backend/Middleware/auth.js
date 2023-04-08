import jwt from "jsonwebtoken";
import dotenv from "dotenv";
dotenv.config();

// auth middleware is used to authenticate the user if the user is valid user 
// whenever request is made it will first go to middleware and if the user is authenticated then only the user is allow to do some task
// next() is used to specify what to do once the user is authenticated

const auth = async (req, res, next) => {
    try {
        const token = req.headers.authorization.split(" ")[1];
        const isLocalToken = token.length < 500;
        let decodeData;
        if (token && isLocalToken) {
            decodeData = jwt.decode(token, process.env.SECRET);
            req.userId = decodeData.id;
        } else {
            decodeData = jwt.decode(token)
            req.userId = decodeData.sub;
        }
        next();
    } catch (error) {
        console.log("this is an error");
        console.log(error);
    }
}

export default auth