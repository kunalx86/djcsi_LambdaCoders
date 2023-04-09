import express from "express"
import bodyParser from "body-parser";
import cors from "cors"
import dotenv from "dotenv"
import mongoose from "mongoose";
import parentRoutes from "./Routes/parent.js";

dotenv.config()


const app = express()
app.use(express.json());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }))
app.use(cors())



app.get("/", (req, res) => {
    res.send("Hello World")
})

app.use("/parent", parentRoutes);


const PORT = process.env.PORT || 8080;

mongoose.connect(process.env.MONGO)
    .then(() => {
        app.listen(PORT, function () {
            console.log("Server started at ", PORT);
        })
    })
    .catch((error) => {
        console.log(error);
    })

