import mongoose from "mongoose";
const parentSchema = new mongoose.Schema({
    firstName: String,
    lastName: String,
    email: String,
    password: String,
    childrens: [mongoose.Schema.Types.ObjectId]
}
    , { timestamps: true }
)

const Parent = mongoose.model("parent", parentSchema);
export default Parent;
