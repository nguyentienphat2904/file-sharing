import mongoose, { Schema } from 'mongoose';
import { PeerModel } from './peer.models';

interface IFile {
    name: string;
    size: number;
    hash_info: string;
    peer: {
        type: {
            address: { type: String, required: true },
            port: { type: String, required: true }
        },
        required: true // Đặt peers là bắt buộc
    }
}

// Define the schema for a file
const FileSchema: Schema = new Schema({
    name: { type: String, required: true },
    size: { type: Number, required: true },
    hash_info: { type: String, required: true, unique: true },
    peer: {
        type: new mongoose.Schema({
            address: { type: String, required: true },
            port: { type: String, required: true }
        }, { _id: false }), // Không tạo _id cho peer
        required: true
    }
}, { versionKey: false });

// Create the Mongoose model
const FileModel = mongoose.model<IFile>('File', FileSchema);

export { FileModel, IFile };