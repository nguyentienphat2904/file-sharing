import mongoose, { mongo, Schema } from "mongoose";
import { FileModel } from "./file.model";

interface IPeer {
    username: string;
    password: string;
    address: string;
    port: string;
    files: mongoose.Types.ObjectId[];
}

const PeerSchema: Schema = new Schema({
    address: { type: String, required: true },
    port: { type: String, required: true },
    username: { type: String, required: true },
    password: { type: String, required: true, unique: true },
    files: [{ type: mongoose.Types.ObjectId, ref: FileModel }]
}, { versionKey: false });

const PeerModel = mongoose.model<IPeer>('Peer', PeerSchema);

export { PeerModel, IPeer }