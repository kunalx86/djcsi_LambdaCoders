import mongoose from "mongoose";
const childrenSchema = new mongoose.Schema({
    firstName: String,
    lastName: String,
    blockedWebsites: [String],
    hours: Number,
    minutes: Number,
    contentFiltering: [String],
    token: String,
    parent: mongoose.Schema.Types.ObjectId

})

const Children = mongoose.model("children", childrenSchema);
export default Children;