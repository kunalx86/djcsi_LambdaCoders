import express from "express";
import { addChildren, signIn, signUp } from "../Controller/parent.js";
import auth from "../Middleware/auth.js";
const parentRoutes = express.Router();


parentRoutes.post("/signUp", signUp);
parentRoutes.post("/signIn", signIn);
parentRoutes.post("/addChildren", auth, addChildren);

export default parentRoutes;
